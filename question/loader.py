import os
import re
import pandas as pd
import random
import language.language as lang_config


# ---------------------------------------------------------------------------
# QuestionProcessor
# ---------------------------------------------------------------------------

class QuestionProcessor:
    def __init__(self, questionType, difficultyIndex, disable_dda=False, is_game_mode=False):
        self.questionType = questionType
        self.widget = None
        self.difficultyIndex = difficultyIndex
        self.df = None
        self.variables = []
        self.oprands = []
        self.rowIndex = 0
        self.retry_count = 0
        self.total_attempts = 0
        self.correct_answers = 0
        self.correct_streak = 0
        self.incorrect_streak = 0
        self.current_performance_rate = 0
        self.current_difficulty = difficultyIndex
        self._used_rows = set()
        self.disable_dda = disable_dda
        self.is_game_mode = is_game_mode
        # Digit-level gate set by GameSession before get_random_question()
        # None = no restriction (non-game / learning mode)
        self.max_digit_level = None

    def get_questions(self):
        if not getattr(self, '_skip_process_file', False):
            self.process_file()
        return self.get_random_question()

    def process_file(self):
        if getattr(self, 'is_game_mode', False):
            file_path = os.path.join(os.getcwd(), "question", "game_ques.xlsx")
            print(f"Processing Game File: {file_path}")

            self.df = pd.read_excel(file_path)
            self.df["difficulty"] = pd.to_numeric(self.df["difficulty"], errors="coerce")
            self.df["type"] = self.df["type"].astype(str).str.strip().str.lower()

            # Parse digits column into a clean integer column for filtering
            if "digits" in self.df.columns:
                self.df["_digit_int"] = (
                    self.df["digits"]
                    .astype(str)
                    .str.extract(r'(\d+)', expand=False)
                    .pipe(pd.to_numeric, errors="coerce")
                    .fillna(1)
                    .astype(int)
                )
            else:
                self.df["_digit_int"] = 1

            valid_difficulties = (
                self.difficultyIndex if isinstance(self.difficultyIndex, list)
                else [self.difficultyIndex]
            )
            level_df = self.df[self.df["difficulty"].isin(valid_difficulties)]
            q_type   = self.questionType.lower().strip()
            typed_df = level_df[level_df["type"] == q_type]

            self.df = (typed_df if len(typed_df) > 0 else level_df).reset_index(drop=True)
            return

        # ── Non-game / learning mode ───────────────────────────────────
        file_path = os.path.join(os.getcwd(), "question", "question.xlsx")
        print(f"Processing file: {file_path}")

        self.df = pd.read_excel(file_path)
        self.df = pd.DataFrame(self.df)

        if self.questionType == "custom":
            print("[Processor] Custom uploaded file detected — skipping filtering.")
            return

        self.df["difficulty"] = pd.to_numeric(self.df["difficulty"], errors="coerce")
        self.df["type"] = self.df["type"].astype(str).str.strip().str.lower()

        print(f"[Processor] Filtering with section: {self.questionType}")

        valid_difficulties = (
            self.difficultyIndex if isinstance(self.difficultyIndex, list)
            else [self.difficultyIndex]
        )
        self.df = self.df[
            (self.df["type"] == self.questionType.lower().strip()) &
            (self.df["difficulty"].isin(valid_difficulties))
        ]
        self.df = self.df.sort_values(by="difficulty", ascending=True)

    def quickplay(self):
        self.process_for_quickplay()
        return self.get_random_question()

    def process_for_quickplay(self):
        file_path = os.path.join(os.getcwd(), "question", "question.xlsx")
        print(f"[QuickPlay] Reloading file fresh: {file_path}")

        df = pd.read_excel(file_path)
        df = pd.DataFrame(df)
        df["type"]       = df["type"].astype(str).str.strip().str.lower()
        df["difficulty"] = pd.to_numeric(df["difficulty"], errors="coerce")

        valid_difficulties = (
            self.difficultyIndex if isinstance(self.difficultyIndex, list)
            else [self.difficultyIndex]
        )
        df = df[df["difficulty"].isin(valid_difficulties)]

        if df.empty:
            print(f"[QuickPlay] No questions found at difficulty {self.difficultyIndex}")
        else:
            print(f"[QuickPlay] {len(df)} questions found at difficulty {self.difficultyIndex}")

        self.df = df.sample(frac=1).reset_index(drop=True)

    def get_random_question(self):
        if self.df is None or self.df.empty:
            return "No questions found.", None

        # Apply per-skill digit gate (game mode only)
        working_df = self.df
        if (
            getattr(self, 'is_game_mode', False)
            and self.max_digit_level is not None
            and "_digit_int" in self.df.columns
        ):
            gated = self.df[self.df["_digit_int"] <= self.max_digit_level]
            if not gated.empty:
                working_df = gated
            # else fall back to full df so we never get stuck with no rows

        all_rows = list(range(len(working_df)))

        if getattr(self, 'is_game_mode', False):
            local_idx = random.choice(all_rows)
        else:
            available = [r for r in all_rows if r not in self._used_rows]
            if not available:
                self._used_rows = set()
                available       = all_rows
            local_idx = random.choice(available)
            self._used_rows.add(local_idx)

        # Store the *actual* DataFrame index so digit logging works with .loc
        self.rowIndex = working_df.index[local_idx]
        row           = working_df.iloc[local_idx]

        variable_string = str(row["operands"])
        input_string    = ''.join(c for c in variable_string if not c.isalpha())
        self.variables  = [c for c in variable_string if c.isalpha()]
        self.oprands    = self.parseInputRange(input_string)

        current_lang = getattr(lang_config, 'selected_language', 'English')

        if current_lang == "हिंदी" and "question_hi" in working_df.columns:
            question_template = str(row["question_hi"])
        elif current_lang == "മലയാളം" and "question_mal" in working_df.columns:
            question_template = str(row["question_mal"])
        else:
            question_template = str(row["question"])

        for i, var in enumerate(self.variables):
            question_template = question_template.replace(f"{{{var}}}", str(self.oprands[i]))

        self.extractAnswer()
        try:
            answer = round(float(self.Pr_answer)) if self.Pr_answer is not None else None
        except (TypeError, ValueError):
            answer = None

        return question_template, answer

    def extractAnswer(self):
        answer_equation = self.getAnswer(self.rowIndex, "equation")
        self.Pr_answer  = str(self.solveEquation(answer_equation))

    def getAnswer(self, row, column):
        ans_equation = str(self.df.loc[row, column])
        ans_equation = ans_equation.replace("×", "*")
        for i in range(len(self.variables)):
            ans_equation = ans_equation.replace(
                f"{{{self.variables[i]}}}", str(self.oprands[i])
            )
        return ans_equation

    def solveEquation(self, ans_equation):
        try:
            return eval(ans_equation)
        except Exception:
            return None

    def removeVariables(self, row, column):
        val = self.df.iloc[row, column]
        return ''.join(c for c in val if not c.isalpha())

    def allVariables(self, row, column):
        val = self.df.iloc[row, column]
        return [c for c in val if c.isalpha()]

    def parseInputRange(self, inputRange):
        operands = []
        current  = ""
        for c in inputRange:
            if c == "*":
                operands.append(int(self.extractType(current)))
                current = ""
            else:
                current += c
        if current:
            operands.append(int(self.extractType(current)))
        return operands

    def extractType(self, inputRange):
        try:
            if "," in inputRange:
                return random.choice(list(map(int, inputRange.split(","))))
            elif ";" in inputRange:
                parts = inputRange.split(";")
                base = int(parts[0])
                if ":" in parts[1]:
                    min_val, max_val = map(int, parts[1].split(":"))
                    result = base * random.randint(min_val, max_val)
                else:
                    result = base * int(parts[1])
                return result if result != 0 else base
            elif ":" in inputRange:
                a, b = map(int, inputRange.split(":"))
                return random.randint(a, b)
            return int(inputRange)
        except Exception:
            return 0

    def replaceVariables(self, rowIndex, columnIndex):
        val = str(self.df.iloc[rowIndex, columnIndex])
        for i, var in enumerate(self.variables):
            val = val.replace(f"{{{var}}}", str(self.oprands[i]))
        return val

    def submit_answer(self, user_answer, correct_answer, time_taken):
        if user_answer is None or str(user_answer).strip() == "":
            return {"valid": False}

        try:
            user_val    = float(user_answer)
            correct_val = float(correct_answer)
        except (ValueError, TypeError):
            return {"valid": False}

        self.total_attempts += 1
        is_correct = (user_val == correct_val)

        if not getattr(self, 'disable_dda', False):
            if is_correct:
                self.correct_answers         += 1
                self.correct_streak          += 1
                self.incorrect_streak         = 0
                self.current_performance_rate += 5
                if time_taken < 5:
                    self.current_performance_rate += 5
                elif time_taken < 10:
                    self.current_performance_rate += 2
            else:
                self.incorrect_streak         += 1
                self.correct_streak            = 0
                self.current_performance_rate -= 10
                if time_taken > 15:
                    self.current_performance_rate -= 5
        else:
            if is_correct:
                self.correct_answers += 1
                self.correct_streak  += 1
                self.incorrect_streak = 0
            else:
                self.incorrect_streak += 1
                self.correct_streak    = 0

        if isinstance(self.current_difficulty, list):
            return {"valid": True, "correct": is_correct}

        if getattr(self, 'disable_dda', False):
            return {"valid": True, "correct": is_correct}

        if self.current_performance_rate >= 30:
            if self.current_difficulty < 5:
                self.current_difficulty      += 1
                self.difficultyIndex          = self.current_difficulty
            self.current_performance_rate     = 0
        elif self.current_performance_rate <= -30:
            if self.current_difficulty > 1:
                self.current_difficulty -= 1
            self.current_performance_rate = 0

        return {"valid": True, "correct": is_correct}

TIER2_SKILLS = ["story", "time", "currency"]

class LinearProgressionSession:
    MAX_QUESTIONS = 20

    def __init__(self, difficulty_index: int):
        self.max_level = 3
        self.level_index = max(0, min(difficulty_index - 1, self.max_level))
        self.difficulty_index = self.level_index
        self.starting_difficulty = self.level_index
        
        import time as _time
        self.session_start_time = _time.time()
        
        import os
        import pandas as pd
        file_path = os.path.join(os.getcwd(), "question", "game_ques.xlsx")
        self.full_df = pd.read_excel(file_path)
        
        self.tier2_skills = TIER2_SKILLS
        self.user_time_factor = 1.0  

        self.correct_streak = 0
        self.wrong_streak = 0
        self.question_count = 0
        self.questions_answered = 0
        
        self.game_active = True
        self.session_time = 90
        self.phase = "Main"
        self.state = "Normal"
        
        self.skill_scores = {s: 50 for s in ["addition", "subtraction", "multiplication", "division"]}
        self.skill_log = {}
        self.recent_performance = []
        self.speed_history = []
        self.level_completed = False
        
        self._build_buckets()
        self.processors = {}
        
    def _build_buckets(self):
        level_df = self.full_df[self.full_df['difficulty'] == self.level_index].copy()
        
        if level_df.empty:
            level_df = self.full_df.copy()
            
        level_df['type_lower'] = level_df['type'].astype(str).str.lower().str.strip()
        main_df = level_df[~level_df['type_lower'].isin(self.tier2_skills)].copy()
        
        self.buckets = []
        self.bucket_to_rows = {}
        
        import re
        def extract_digit(raw):
            m = re.search(r'(\d+)', str(raw))
            return int(m.group(1)) if m else 1
            
        main_df['_digit_int'] = main_df['digits'].apply(extract_digit)
        self.main_df = main_df
        
        for (b_type, b_digits), group in main_df.groupby(['type_lower', '_digit_int']):
            bucket_tuple = (b_type, b_digits)
            if bucket_tuple not in self.buckets:
                self.buckets.append(bucket_tuple)
                self.bucket_to_rows[bucket_tuple] = list(group.index)
            
        op_order = {"addition": 0, "subtraction": 1, "multiplication": 2, "division": 3}
        self.buckets.sort(key=lambda b: (op_order.get(b[0], 99), b[1]))
        print("[BUCKET ORDER]", self.buckets)
        
        if not self.buckets:
            self.buckets = [("addition", 1)]
            self.bucket_to_rows = {("addition", 1): list(self.full_df.index)[:10]}
            
        self.bucket_index = 0
        self.used_questions = {b: set() for b in self.buckets}
        self.recent_patterns = []

    def get_ideal_time(self, operation: str, digits: int) -> float:
        base_time = {
            "addition": 4,
            "subtraction": 5, 
            "multiplication": 7, 
            "division": 9
        }
        b_time = base_time.get(operation.lower(), 5)
        return (b_time + (digits * 2)) * 1.5

    def is_session_complete(self):
        return self.question_count >= self.MAX_QUESTIONS or not self.game_active

    def set_finale(self):
        self.phase = "Finale"

    def get_phase(self):
        return self.phase

    def _get_tier2_processor(self, skill, difficulty):
        from question.loader import QuestionProcessor
        key = (skill, difficulty)
        
        def _get_filtered_df(diff):
            skill_lower = skill.lower().strip()
            df_slice = self.full_df[
                (self.full_df['difficulty'] == diff) & 
                (self.full_df['type'].astype(str).str.lower().str.strip() == skill_lower)
            ].copy()
            if df_slice.empty:
                df_slice = self.full_df[
                    (self.full_df['difficulty'].isin([0, 1, 2, 3])) & 
                    (self.full_df['type'].astype(str).str.lower().str.strip() == skill_lower)
                ].copy()
            if "digits" in df_slice.columns and "_digit_int" not in df_slice.columns:
                import re
                df_slice["_digit_int"] = df_slice["digits"].apply(
                    lambda raw: int(re.search(r'(\d+)', str(raw)).group(1)) if re.search(r'(\d+)', str(raw)) else 1
                )
            elif "_digit_int" not in df_slice.columns:
                df_slice["_digit_int"] = 1
            return df_slice.reset_index(drop=True)

        if key not in self.processors:
            p = QuestionProcessor(skill, difficulty, disable_dda=True, is_game_mode=True)
            p.df = _get_filtered_df(difficulty)
            p._skip_process_file = True
            self.processors[key] = p
        else:
            p = self.processors[key]
            if p.difficultyIndex != difficulty:
                p.difficultyIndex = difficulty
                p.df = _get_filtered_df(difficulty)
        return p

    def get_next_question(self):
        self.question_count += 1
        
        if self.question_count % 4 == 0:
            import random
            t2 = random.choice(self.tier2_skills)
            self.current_skill = t2
            p = self._get_tier2_processor(t2, self.level_index)
            self.current_processor = p
            self._is_tier2_interleave = True
            return p

        self._is_tier2_interleave = False
        import random
        from question.loader import QuestionProcessor
        
        self.bucket_index = max(0, min(self.bucket_index, len(self.buckets) - 1))
        bucket = self.buckets[self.bucket_index]
        
        available_rows = [r for r in self.bucket_to_rows[bucket] if r not in self.used_questions[bucket]]
        
        if not available_rows:
            self.used_questions[bucket].clear()
            available_rows = list(self.bucket_to_rows[bucket])
            
        valid_rows = []
        for r in available_rows:
            try:
                pattern = str(self.main_df.loc[r, 'operands']).strip()
                if pattern not in self.recent_patterns[-1:]:
                    valid_rows.append(r)
            except KeyError:
                valid_rows.append(r)
                
        if not valid_rows and available_rows:
            valid_rows = available_rows 
            
        if not valid_rows:
             chosen_row_index = self.main_df.index[0]
        else:
             chosen_row_index = random.choice(valid_rows)

        self.used_questions[bucket].add(chosen_row_index)
        try:
             pattern = str(self.main_df.loc[chosen_row_index, 'operands']).strip()
             self.recent_patterns.append(pattern)
        except KeyError:
             self.recent_patterns.append("N/A")
        
        self.current_skill = bucket[0]
        self.current_digits = bucket[1]

        print(f"[BUCKET PROGRESSION] Serving `{self.current_skill}` {self.current_digits}d from bucket {self.bucket_index + 1}/{len(self.buckets)}")

        p = QuestionProcessor(self.current_skill, self.level_index + 1, disable_dda=True, is_game_mode=True)
        try:
            p.df = self.main_df.loc[[chosen_row_index]].reset_index(drop=True)
        except Exception:
            p.df = self.main_df.iloc[[0]].reset_index(drop=True)

        p.rowIndex = 0
        p._used_rows = set()
        p._skip_process_file = True
        
        self.current_processor = p
        return p

    def submit_answer(self, skill_type, is_correct, time_taken, replay_count=0):
        skill_type = str(skill_type).lower().strip()
        self.questions_answered += 1
        
        if skill_type not in self.skill_log:
            self.skill_log[skill_type] = {'correct': 0, 'wrong': 0, 'times': [], 'weak_digits': []}

        if getattr(self, '_is_tier2_interleave', False):
            if is_correct:
                self.skill_log[skill_type]['correct'] += 1
                self.recent_performance.append("excellent")
            else:
                self.skill_log[skill_type]['wrong'] += 1
                self.recent_performance.append("incorrect")
            self.speed_history.append("NORMAL")
            return

        ideal = self.get_ideal_time(getattr(self, 'current_skill', skill_type), getattr(self, 'current_digits', 1))
        adjusted_time = ideal * self.user_time_factor

        if time_taken <= 0.8 * adjusted_time:
            speed = "FAST"
            perf_log = "excellent"
        elif time_taken <= 1.5 * adjusted_time:
            speed = "NORMAL"
            perf_log = "good"
        else:
            speed = "SLOW"
            perf_log = "slow"

        if replay_count >= 1 and speed == "FAST":
            speed = "NORMAL"
        if replay_count >= 2:
            speed = "NORMAL"

        self.speed_history.append(speed)
        delta = 0

        if is_correct:
            self.correct_streak += 1
            self.wrong_streak = 0
            self.skill_log[skill_type]['correct'] += 1
            self.skill_log[skill_type]['times'].append(time_taken)
            self.recent_performance.append(perf_log)
            delta = 5

            if speed == "SLOW":
                 self.user_time_factor += 0.1

            if self.correct_streak >= 2:
                 self.bucket_index += 1
                 self._reset_streaks()

        else:
            self.wrong_streak += 1
            self.correct_streak = 0
            self.skill_log[skill_type]['wrong'] += 1
            self.recent_performance.append("incorrect")
            delta = -5

            if self.wrong_streak >= 2:
                self.bucket_index = max(0, self.bucket_index - 1)

        if skill_type in self.skill_scores:
            self.skill_scores[skill_type] = max(0, min(100, self.skill_scores[skill_type] + delta))
            
        self._check_level_transitions()

    def _reset_streaks(self):
         self.correct_streak = 0
         self.wrong_streak = 0

    def _check_level_transitions(self):
        if self.bucket_index >= len(self.buckets):
            self.game_active = False
            self.level_completed = True
            return

        elif self.bucket_index == 0 and self.wrong_streak >= 3 and self.speed_history and self.speed_history[-1] == "SLOW":
            if self.level_index > 0:
                self.level_index -= 1
                self.difficulty_index = self.level_index
                self._build_buckets()
                self._reset_streaks()
            else:
                self.wrong_streak = 0

        self.bucket_index = max(0, min(self.bucket_index, len(self.buckets) - 1))

    def generate_breakdown(self):
        from language.language import tr
        parts = []
        for q_type, stats in sorted(self.skill_log.items()):
            total = stats['correct'] + stats['wrong']
            if total == 0: continue
            parts.append(f"{tr(q_type.capitalize())}: {stats['correct']}/{total}")
        return "  ·  ".join(parts) if parts else ""

    def generate_summary(self):
        from language.language import tr
        total = self.questions_answered
        correct = sum(s['correct'] for s in self.skill_log.values())
        if total == 0:
            return tr("Session complete!")
        pct = int((correct / total) * 100)
        elapsed = int(__import__('time').time() - self.session_start_time)
        mins = elapsed // 60
        secs = elapsed % 60
        time_str = f"{mins}m {secs}s" if mins > 0 else f"{secs}s"
        if getattr(self, 'level_completed', False):
            mood = tr("Level Complete! Outstanding job!")
        elif pct >= 80:
            mood = tr("Great job!")
        elif pct >= 60:
            mood = tr("Good effort!")
        else:
            mood = tr("Keep practicing!")
        return f"{mood} {correct}/{total} correct · {time_str}"

    def generate_report(self):
        return self.generate_breakdown() + ". " + self.generate_summary()

    @property
    def digit_level(self):
         return { "addition":self.level_index+1, "subtraction":self.level_index+1, "multiplication":self.level_index+1, "division":self.level_index+1 }
