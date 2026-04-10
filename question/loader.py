
import os
import re
import random
import pandas as pd
import language.language as lang_config


# ---------------------------------------------------------------------------
# Concept transition table  (mirrors game_ques.xlsx forward/backward columns)
# ---------------------------------------------------------------------------

CONCEPT_TRANSITIONS = {
    'addition_no_carry':          {'forward': 'addition_with_carry',        'backward': None},
    'addition_with_carry':        {'forward': 'multi_digit_multiplication', 'backward': 'addition_no_carry'},
    'subtraction_no_borrow':      {'forward': 'subtraction_with_borrow',    'backward': None},
    'subtraction_with_borrow':    {'forward': 'multi_digit_division',       'backward': 'subtraction_no_borrow'},
    'multiplication_basic':       {'forward': 'multi_digit_multiplication', 'backward': 'addition_with_carry'},
    'multi_digit_multiplication': {'forward': 'mixed_operations',           'backward': 'multiplication_basic'},
    'division_basic':             {'forward': 'multi_digit_division',       'backward': 'multiplication_basic'},
    'multi_digit_division':       {'forward': 'mixed_operations',           'backward': 'division_basic'},
    'word_problems':              {'forward': 'mixed_operations',           'backward': 'addition_with_carry'},
    'time_problems':              {'forward': 'mixed_operations',           'backward': 'addition_with_carry'},
    'currency_problems':          {'forward': 'mixed_operations',           'backward': 'multi_digit_multiplication'},
    'mixed_operations':           {'forward': None,                         'backward': 'multi_digit_multiplication'},
}

# ---------------------------------------------------------------------------
# Bridge question generator
# ---------------------------------------------------------------------------

def generate_bridge_questions(concept: str) -> list[dict]:
    questions = []
    if concept in ('multiplication_basic', 'multi_digit_multiplication'):
        for _ in range(2):
            factor = random.randint(2, 5)
            times  = random.randint(2, 4)
            terms  = [factor] * times
            q_str  = ' + '.join(str(t) for t in terms) + ' = ?'
            questions.append({'question': q_str, 'answer': sum(terms), 'concept': 'addition_with_carry'})
    elif concept in ('division_basic', 'multi_digit_division'):
        for _ in range(2):
            divisor = random.randint(2, 5)
            times   = random.randint(2, 4)
            start   = divisor * times
            q_str   = str(start) + ' - ' + ' - '.join(str(divisor) for _ in range(times)) + ' = ?'
            questions.append({'question': q_str, 'answer': 0, 'concept': 'subtraction_no_borrow'})
    elif concept == 'subtraction_with_borrow':
        for _ in range(2):
            b = random.randint(1, 4)
            a = random.randint(b, 9)
            questions.append({'question': f'{a} - {b} = ?', 'answer': a - b, 'concept': 'subtraction_no_borrow'})
    elif concept == 'addition_with_carry':
        for _ in range(2):
            a = random.randint(1, 4)
            b = random.randint(1, 5 - a)
            questions.append({'question': f'{a} + {b} = ?', 'answer': a + b, 'concept': 'addition_no_carry'})
    return questions


# ---------------------------------------------------------------------------
# QuestionProcessor
# ---------------------------------------------------------------------------

class QuestionProcessor:
    def __init__(self, questionType, difficultyIndex, disable_dda=False,
                 is_game_mode=False, preloaded_df=None):
        self.questionType          = questionType
        self.widget                = None
        self.difficultyIndex       = difficultyIndex
        self.df                    = None
        self.variables             = []
        self.oprands               = []
        self.rowIndex              = 0
        self.retry_count           = 0
        self.total_attempts        = 0
        self.correct_answers       = 0
        self.correct_streak        = 0
        self.incorrect_streak      = 0
        self.current_performance_rate = 0
        self.current_difficulty    = difficultyIndex
        self._used_rows            = set()
        self.disable_dda           = disable_dda
        self.is_game_mode          = is_game_mode
        self.max_digit_level       = None
        self._skip_process_file    = False

        if preloaded_df is not None:
            self.df                  = preloaded_df.reset_index(drop=True)
            self._skip_process_file  = True

    # ── File loading ──────────────────────────────────────────────────────────

    def get_questions(self):
        if not self._skip_process_file:
            self.process_file()
        return self.get_random_question()

    def process_file(self):
        if self.is_game_mode:
            file_path = os.path.join(os.getcwd(), "question", "game_ques.xlsx")
            print(f"[Processor] Game file: {file_path}")

            df = pd.read_excel(file_path)
            # FIX: normalise type to lower-case immediately
            df["type"]       = df["type"].astype(str).str.strip().str.lower()
            df["digits"]     = df["digits"].astype(str).str.strip().str.lower()
            df["difficulty"] = pd.to_numeric(df["difficulty"], errors="coerce").fillna(0).astype(int)
            df["label"]      = df["label"].astype(str).str.strip()

            if "digits" in df.columns:
                df["_digit_int"] = (
                    df["digits"]
                    .str.extract(r'(\d+)', expand=False)
                    .pipe(pd.to_numeric, errors="coerce")
                    .fillna(1).astype(int)
                )
            else:
                df["_digit_int"] = 1

            valid_difficulties = (
                self.difficultyIndex if isinstance(self.difficultyIndex, list)
                else [self.difficultyIndex]
            )
            q_type   = self.questionType.lower().strip()
            level_df = df[df["difficulty"].isin(valid_difficulties)]
            typed_df = level_df[level_df["type"] == q_type]

            # FIX: always fall back gracefully
            if not typed_df.empty:
                self.df = typed_df.reset_index(drop=True)
            elif not level_df.empty:
                self.df = level_df.reset_index(drop=True)
            else:
                self.df = df.reset_index(drop=True)
            return

        # ── Non-game / learning mode ──────────────────────────────────────────
        file_path = os.path.join(os.getcwd(), "question", "question.xlsx")
        print(f"[Processor] Learning file: {file_path}")

        df = pd.read_excel(file_path)

        if self.questionType == "custom":
            self.df = df
            return

        df["difficulty"] = pd.to_numeric(df["difficulty"], errors="coerce")
        df["type"]       = df["type"].astype(str).str.strip().str.lower()

        valid_difficulties = (
            self.difficultyIndex if isinstance(self.difficultyIndex, list)
            else [self.difficultyIndex]
        )
        filtered = df[
            (df["type"] == self.questionType.lower().strip())
            & (df["difficulty"].isin(valid_difficulties))
        ]
        self.df = filtered.sort_values("difficulty", ascending=True).reset_index(drop=True)

    def quickplay(self):
        self.process_for_quickplay()
        return self.get_random_question()

    def process_for_quickplay(self):
        file_path = os.path.join(os.getcwd(), "question", "question.xlsx")
        df = pd.read_excel(file_path)
        df["type"]       = df["type"].astype(str).str.strip().str.lower()
        df["difficulty"] = pd.to_numeric(df["difficulty"], errors="coerce")
        valid_difficulties = (
            self.difficultyIndex if isinstance(self.difficultyIndex, list)
            else [self.difficultyIndex]
        )
        df = df[df["difficulty"].isin(valid_difficulties)]
        self.df = df.sample(frac=1).reset_index(drop=True)

    # ── Question selection ────────────────────────────────────────────────────

    def get_random_question(self):
        if self.df is None or self.df.empty:
            return "No questions found.", None

        working_df = self.df

        if (
            self.is_game_mode
            and self.max_digit_level is not None
            and "_digit_int" in self.df.columns
        ):
            gated = self.df[self.df["_digit_int"] <= self.max_digit_level]
            if not gated.empty:
                working_df = gated

        all_rows = list(range(len(working_df)))

        if self.is_game_mode:
            local_idx = random.choice(all_rows)
        else:
            available = [r for r in all_rows if r not in self._used_rows]
            if not available:
                self._used_rows = set()
                available = all_rows
            local_idx = random.choice(available)
            self._used_rows.add(local_idx)

        # FIX: use iloc (positional) so stale rowIndex doesn't cause KeyError
        row = working_df.iloc[local_idx]
        self.rowIndex = local_idx   # store positional for extractAnswer

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

        # Replace NaN templates with English fallback
        if question_template in ("nan", "None", ""):
            question_template = str(row["question"])

        for i, var in enumerate(self.variables):
            if i < len(self.oprands):
                question_template = question_template.replace(f"{{{var}}}", str(self.oprands[i]))

        # Store working_df for extractAnswer so we use the same slice
        self._working_df = working_df
        self.extractAnswer()

        try:
            answer = round(float(self.Pr_answer)) if self.Pr_answer is not None else None
        except (TypeError, ValueError):
            answer = None

        return question_template, answer

    # ── Answer handling ───────────────────────────────────────────────────────

    def extractAnswer(self):
        answer_equation = self.getAnswer(self.rowIndex, "equation")
        self.Pr_answer  = str(self.solveEquation(answer_equation))

    def getAnswer(self, row_idx: int, column: str) -> str:
        # FIX: use _working_df (positional) to avoid stale index KeyError
        df = getattr(self, '_working_df', self.df)
        if df is None or df.empty:
            return "0"
        row_idx = min(row_idx, len(df) - 1)
        ans_equation = str(df.iloc[row_idx][column])
        ans_equation = ans_equation.replace("×", "*")
        for i in range(len(self.variables)):
            if i < len(self.oprands):
                ans_equation = ans_equation.replace(f"{{{self.variables[i]}}}", str(self.oprands[i]))
        return ans_equation

    def solveEquation(self, ans_equation: str):
        try:
            return eval(ans_equation)
        except Exception:
            return None

    def removeVariables(self, row, column):
        val = self.df.iloc[row][column]
        return ''.join(c for c in str(val) if not c.isalpha())

    def allVariables(self, row, column):
        val = self.df.iloc[row][column]
        return [c for c in str(val) if c.isalpha()]

    def parseInputRange(self, inputRange: str) -> list[int]:
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

    def extractType(self, inputRange: str):
        try:
            if "," in inputRange:
                return random.choice(list(map(int, inputRange.split(","))))
            elif ";" in inputRange:
                parts  = inputRange.split(";")
                base   = int(parts[0])
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

    def replaceVariables(self, rowIndex: int, columnIndex: int) -> str:
        val = str(self.df.iloc[rowIndex].iloc[columnIndex])
        for i, var in enumerate(self.variables):
            if i < len(self.oprands):
                val = val.replace(f"{{{var}}}", str(self.oprands[i]))
        return val

    def submit_answer(self, user_answer, correct_answer, time_taken, replay_count=0):
        if user_answer is None or str(user_answer).strip() == "":
            return {"valid": False}
        try:
            user_val    = float(user_answer)
            correct_val = float(correct_answer)
        except (ValueError, TypeError):
            return {"valid": False}

        self.total_attempts += 1
        is_correct = (user_val == correct_val)

        if not self.disable_dda:
            if is_correct:
                self.correct_answers          += 1
                self.correct_streak           += 1
                self.incorrect_streak          = 0
                self.current_performance_rate += 5
                if time_taken < 5:   self.current_performance_rate += 5
                elif time_taken < 10: self.current_performance_rate += 2
            else:
                self.incorrect_streak         += 1
                self.correct_streak            = 0
                self.current_performance_rate -= 10
                if time_taken > 15: self.current_performance_rate -= 5
        else:
            if is_correct:
                self.correct_answers  += 1
                self.correct_streak   += 1
                self.incorrect_streak  = 0
            else:
                self.incorrect_streak += 1
                self.correct_streak    = 0

        if isinstance(self.current_difficulty, list):
            return {"valid": True, "correct": is_correct}

        if self.disable_dda:
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


# ---------------------------------------------------------------------------
# Concept lookup helpers
# ---------------------------------------------------------------------------

def get_concept_for_row(row: pd.Series) -> str:
    t = str(row.get('type', '')).strip().lower()
    d = int(row.get('difficulty', 0))
    if t == 'addition':       return 'addition_no_carry' if d == 0 else 'addition_with_carry'
    if t == 'subtraction':    return 'subtraction_no_borrow' if d == 0 else 'subtraction_with_borrow'
    if t == 'multiplication': return 'multiplication_basic' if d == 0 else 'multi_digit_multiplication'
    if t == 'division':       return 'division_basic' if d == 0 else 'multi_digit_division'
    if t == 'story':          return 'word_problems'
    if t == 'time':           return 'time_problems'
    if t == 'currency':       return 'currency_problems'
    if t == 'mixed':          return 'mixed_operations'
    return 'unknown'


# ---------------------------------------------------------------------------
# Tier-2 skill list
# ---------------------------------------------------------------------------

TIER2_SKILLS = ["story", "time", "currency"]


# ---------------------------------------------------------------------------
# LinearProgressionSession
# ---------------------------------------------------------------------------

class LinearProgressionSession:
    MAX_QUESTIONS = 20
    BRIDGE_LENGTH = 2

    def __init__(self, difficulty_index: int):
        self.max_level = 3

        # FIX: user difficulty is 1-based (1,2,3,4); Excel difficulty is 0-based (0,1,2,3)
        self.level_index           = max(0, min(difficulty_index - 1, self.max_level))
        self.difficulty_index      = self.level_index
        self.starting_difficulty   = self.level_index

        import time as _time
        self.session_start_time = _time.time()

        # ── Load Excel ────────────────────────────────────────────────────────
        file_path    = os.path.join(os.getcwd(), "question", "game_ques.xlsx")
        full_df      = pd.read_excel(file_path)
        # FIX: normalise type column immediately
        full_df["type"]       = full_df["type"].astype(str).str.strip().str.lower()
        full_df["digits"]     = full_df["digits"].astype(str).str.strip().str.lower()
        full_df["label"]      = full_df["label"].astype(str).str.strip()
        full_df["difficulty"] = pd.to_numeric(full_df["difficulty"], errors="coerce").fillna(0).astype(int)
        self.full_df = full_df

        self.tier2_skills     = TIER2_SKILLS
        self.user_time_factor = 1.0

        self.correct_streak  = 0
        self.wrong_streak    = 0
        self.question_count  = 0
        self.questions_answered = 0

        self._recently_interleaved        = False
        self.questions_in_current_concept = 0
        self._current_concept_tracked     = None

        self.game_active  = True
        self.session_time = 90
        self.phase        = "Main"
        self.state        = "Normal"

        self.skill_scores       = {s: 50 for s in ["addition", "subtraction", "multiplication", "division"]}
        self.skill_log          = {}
        self.recent_performance = []
        self.speed_history      = []
        self.level_completed    = False

        self._bridge_queue: list[dict] = []
        self._is_bridge = False

        self._build_buckets()
        self.processors = {}

    # ── Bucket construction ───────────────────────────────────────────────────

    def _build_buckets(self):
        # FIX: filter by self.level_index which is correctly 0-based Excel difficulty
        level_df = self.full_df[self.full_df["difficulty"] == self.level_index].copy()
        if level_df.empty:
            # fallback: try difficulty 0
            level_df = self.full_df[self.full_df["difficulty"] == 0].copy()
        if level_df.empty:
            level_df = self.full_df.copy()

        main_df = level_df[~level_df["type"].isin(self.tier2_skills)].copy()

        def extract_digit(raw):
            m = re.search(r'(\d+)', str(raw))
            return int(m.group(1)) if m else 1

        main_df["_digit_int"] = main_df["digits"].apply(extract_digit)
        self.main_df = main_df

        self.buckets        = []
        self.bucket_to_rows = {}

        for (b_type, b_digits), group in main_df.groupby(["type", "_digit_int"]):
            bucket_tuple = (b_type, int(b_digits))
            if bucket_tuple not in self.buckets:
                self.buckets.append(bucket_tuple)
                self.bucket_to_rows[bucket_tuple] = list(group.index)

        op_order = {"addition": 0, "subtraction": 1, "multiplication": 2, "division": 3}
        self.buckets.sort(key=lambda b: (op_order.get(b[0], 99), b[1]))
        print(f"[BUCKET ORDER] difficulty={self.level_index}: {self.buckets}")

        if not self.buckets:
            # Absolute fallback
            self.buckets = [("addition", 1)]
            self.bucket_to_rows = {("addition", 1): list(self.full_df.index)[:10]}

        self.bucket_index    = 0
        self.used_questions  = {b: set() for b in self.buckets}
        self.recent_patterns = []

    # ── Timing helpers ────────────────────────────────────────────────────────

    def get_ideal_time(self, operation: str, digits: int) -> float:
        base = {"addition": 4, "subtraction": 5, "multiplication": 7, "division": 9}
        return (base.get(operation.lower(), 5) + digits * 2) * 1.5

    # ── Session state ─────────────────────────────────────────────────────────

    def is_session_complete(self) -> bool:
        return self.question_count >= self.MAX_QUESTIONS or not self.game_active

    def set_finale(self):
        self.phase = "Finale"

    def get_phase(self) -> str:
        return self.phase

    # ── Tier-2 processor ──────────────────────────────────────────────────────

    def _get_tier2_processor(self, skill: str, difficulty: int):
        key = (skill, difficulty)

        def _filtered(diff):
            df_slice = self.full_df[
                (self.full_df["difficulty"] == diff)
                & (self.full_df["type"] == skill.lower())
            ].copy()
            if df_slice.empty:
                df_slice = self.full_df[self.full_df["type"] == skill.lower()].copy()
            if "_digit_int" not in df_slice.columns:
                df_slice["_digit_int"] = df_slice["digits"].apply(
                    lambda raw: int(re.search(r'(\d+)', str(raw)).group(1))
                    if re.search(r'(\d+)', str(raw)) else 1
                )
            return df_slice.reset_index(drop=True)

        if key not in self.processors:
            p = QuestionProcessor(skill, difficulty, disable_dda=True, is_game_mode=True,
                                  preloaded_df=_filtered(difficulty))
            self.processors[key] = p
        else:
            p = self.processors[key]
            if p.difficultyIndex != difficulty:
                p.difficultyIndex = difficulty
                p.df = _filtered(difficulty)
        return p

    # ── Question delivery ─────────────────────────────────────────────────────

    def get_next_question(self):
        """Return either a bridge dict or a QuestionProcessor."""
        # ── Drain bridge queue first ──────────────────────────────────────────
        if self._bridge_queue:
            bridge_q        = self._bridge_queue.pop(0)
            self._is_bridge = True
            self.question_count += 1
            print(f"[BRIDGE] Serving: {bridge_q['question']} (concept={bridge_q['concept']})")
            return bridge_q

        self._is_bridge = False
        self.question_count += 1

        # ── Tier-2 interleave ─────────────────────────────────────────────────
        if (
            self.correct_streak >= 3
            and self.wrong_streak == 0
            and self.questions_in_current_concept >= 3
            and not self._recently_interleaved
            and random.random() < 0.20
        ):
            t2 = random.choice(self.tier2_skills)
            self.current_skill        = t2
            p  = self._get_tier2_processor(t2, self.level_index)
            self.current_processor    = p
            self._is_tier2_interleave = True
            self._recently_interleaved = True
            return p

        self._is_tier2_interleave = False

        # ── Guard bucket_index ────────────────────────────────────────────────
        # FIX: clamp so we never go out of bounds mid-question
        self.bucket_index = max(0, min(self.bucket_index, len(self.buckets) - 1))
        bucket = self.buckets[self.bucket_index]

        available_rows = [r for r in self.bucket_to_rows[bucket]
                          if r not in self.used_questions[bucket]]
        if not available_rows:
            self.used_questions[bucket].clear()
            available_rows = list(self.bucket_to_rows[bucket])

        valid_rows = []
        for r in available_rows:
            try:
                pattern = str(self.main_df.loc[r, "operands"]).strip()
                if pattern not in self.recent_patterns[-1:]:
                    valid_rows.append(r)
            except KeyError:
                valid_rows.append(r)
        if not valid_rows:
            valid_rows = available_rows

        chosen_row_index = random.choice(valid_rows) if valid_rows else self.main_df.index[0]
        self.used_questions[bucket].add(chosen_row_index)

        try:
            self.recent_patterns.append(str(self.main_df.loc[chosen_row_index, "operands"]).strip())
        except KeyError:
            self.recent_patterns.append("N/A")

        self.current_skill  = bucket[0]
        self.current_digits = bucket[1]

        try:
            row_data = self.main_df.loc[chosen_row_index]
            self.current_concept = get_concept_for_row(row_data)
            self.current_label   = str(row_data.get("label", "")).strip()
        except Exception:
            self.current_concept = "addition_no_carry"
            self.current_label   = ""

        # Track concept run-length for interleave logic
        if self._current_concept_tracked != self.current_concept:
            self._current_concept_tracked     = self.current_concept
            self.questions_in_current_concept = 1
            self._recently_interleaved        = False
        else:
            self.questions_in_current_concept += 1

        print(f"[BUCKET] `{self.current_skill}` {self.current_digits}d | "
              f"bucket {self.bucket_index + 1}/{len(self.buckets)} | concept={self.current_concept}")

        # Build processor from the exact label rows
        p = QuestionProcessor(self.current_skill, self.level_index,
                              disable_dda=True, is_game_mode=True)

        # FIX: robust label match — use str comparison after normalising
        if "label" in self.main_df.columns and self.current_label:
            label_df = self.main_df[self.main_df["label"].str.strip() == self.current_label]
            if not label_df.empty:
                p.df = label_df.copy().reset_index(drop=True)
            else:
                # bucket fallback
                bucket_df = self.main_df[
                    (self.main_df["type"] == self.current_skill)
                ]
                p.df = (bucket_df if not bucket_df.empty else self.main_df).copy().reset_index(drop=True)
        else:
            try:
                p.df = self.main_df.loc[[chosen_row_index]].reset_index(drop=True)
            except Exception:
                p.df = self.main_df.iloc[[0]].reset_index(drop=True) if not self.main_df.empty else pd.DataFrame()

        p.rowIndex           = 0
        p._used_rows         = set()
        p._skip_process_file = True
        self.current_processor = p
        return p

    # ── Answer submission ─────────────────────────────────────────────────────

    def submit_answer(self, skill_type: str, is_correct: bool, time_taken: float, replay_count: int = 0):
        skill_type = str(skill_type).lower().strip()
        self.questions_answered += 1

        if skill_type not in self.skill_log:
            self.skill_log[skill_type] = {"correct": 0, "wrong": 0, "times": [], "weak_digits": []}

        if self._is_bridge:
            if is_correct: self.skill_log[skill_type]["correct"] += 1
            else:          self.skill_log[skill_type]["wrong"]   += 1
            self.speed_history.append("NORMAL")
            self.recent_performance.append("excellent" if is_correct else "incorrect")
            return

        if getattr(self, "_is_tier2_interleave", False):
            if is_correct: self.skill_log[skill_type]["correct"] += 1
            else:          self.skill_log[skill_type]["wrong"]   += 1
            self.speed_history.append("NORMAL")
            self.recent_performance.append("excellent" if is_correct else "incorrect")
            return

        # ── Speed classification ──────────────────────────────────────────────
        ideal = self.get_ideal_time(
            getattr(self, "current_skill", skill_type),
            getattr(self, "current_digits", 1)
        )
        adjusted = ideal * self.user_time_factor
        if time_taken <= 0.8 * adjusted:   speed, perf = "FAST",   "excellent"
        elif time_taken <= 1.5 * adjusted:  speed, perf = "NORMAL", "good"
        else:                               speed, perf = "SLOW",   "slow"

        if replay_count >= 1 and speed == "FAST": speed = "NORMAL"
        if replay_count >= 2:                      speed = "NORMAL"

        self.speed_history.append(speed)
        delta = 0

        if is_correct:
            self.correct_streak += 1
            self.wrong_streak    = 0
            self.skill_log[skill_type]["correct"] += 1
            self.skill_log[skill_type]["times"].append(time_taken)
            self.recent_performance.append(perf)
            delta = 5
            if speed == "SLOW":
                self.user_time_factor += 0.1
            # FIX: guard advancement so bucket_index can't exceed last valid index
            if self.correct_streak >= 2:
                next_idx = self.bucket_index + 1
                if next_idx < len(self.buckets):
                    self.bucket_index = next_idx
                else:
                    # All buckets done → session ends naturally via is_session_complete
                    self.game_active = False
                self._reset_streaks()
        else:
            self.wrong_streak   += 1
            self.correct_streak  = 0
            self._recently_interleaved = False
            self.skill_log[skill_type]["wrong"] += 1
            self.recent_performance.append("incorrect")
            delta = -5

            if self.wrong_streak >= 2:
                concept = getattr(self, "current_concept", None)
                if concept:
                    bridge_qs = generate_bridge_questions(concept)
                    for bq in bridge_qs:
                        bq["is_bridge"] = True
                    if bridge_qs:
                        self._bridge_queue = bridge_qs
                        print(f"[BRIDGE] Queued {len(bridge_qs)} bridge Qs for '{concept}'")

                self.bucket_index = max(0, self.bucket_index - 1)

        if skill_type in self.skill_scores:
            self.skill_scores[skill_type] = max(0, min(100, self.skill_scores[skill_type] + delta))

        self._check_level_transitions()

    # ── Progression helpers ───────────────────────────────────────────────────

    def _reset_streaks(self):
        self.correct_streak = 0
        self.wrong_streak   = 0

    def _check_level_transitions(self):
        # FIX: game_active already set to False in submit_answer when all buckets done
        if not self.game_active:
            self.level_completed = True
            return

        # FIX: clamp bucket_index after any mutation
        self.bucket_index = max(0, min(self.bucket_index, len(self.buckets) - 1))

        if (
            self.bucket_index == 0
            and self.wrong_streak >= 3
            and self.speed_history
            and self.speed_history[-1] == "SLOW"
        ):
            if self.level_index > 0:
                self.level_index      -= 1
                self.difficulty_index  = self.level_index
                self._build_buckets()
                self._reset_streaks()
            else:
                self.wrong_streak = 0

    # ── Reporting ─────────────────────────────────────────────────────────────

    def generate_breakdown(self) -> str:
        from language.language import tr
        parts = []
        for q_type, stats in sorted(self.skill_log.items()):
            total = stats["correct"] + stats["wrong"]
            if total == 0:
                continue
            parts.append(f"{tr(q_type.capitalize())}: {stats['correct']}/{total}")
        return "  ·  ".join(parts) if parts else ""

    def generate_summary(self) -> str:
        from language.language import tr
        total   = self.questions_answered
        correct = sum(s["correct"] for s in self.skill_log.values())
        if total == 0:
            return tr("Session complete!")
        pct     = int((correct / total) * 100)
        elapsed = int(__import__("time").time() - self.session_start_time)
        mins, secs = elapsed // 60, elapsed % 60
        time_str   = f"{mins}m {secs}s" if mins > 0 else f"{secs}s"
        if getattr(self, "level_completed", False):
            mood = tr("Level Complete! Outstanding job!")
        elif pct >= 80: mood = tr("Great job!")
        elif pct >= 60: mood = tr("Good effort!")
        else:           mood = tr("Keep practicing!")
        return f"{mood} {correct}/{total} correct · {time_str}"

    def generate_report(self) -> str:
        return self.generate_breakdown() + ". " + self.generate_summary()

    @property
    def digit_level(self) -> dict:
        return {k: self.level_index + 1 for k in
                ("addition", "subtraction", "multiplication", "division")}