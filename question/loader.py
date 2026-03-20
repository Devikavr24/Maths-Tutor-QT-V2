import os
import pandas as pd
import random
import language.language as lang_config

class QuestionProcessor:
    def __init__(self, questionType, difficultyIndex):
        self.questionType = questionType
        self.widget = None
        self.difficultyIndex = difficultyIndex
        self.df = None
        self.variables = []
        self.oprands = []
        self.rowIndex = 0
        self.retry_count = 0
        # DDA-related fields
        self.total_attempts = 0
        self.correct_answers = 0
        self.correct_streak = 0
        self.incorrect_streak = 0
        self.current_performance_rate = 0
        self.current_difficulty = difficultyIndex 

    def get_questions(self):
        if hasattr(self, '_prepared_question') and self._prepared_question:
            q = self._prepared_question
            a = self._prepared_answer
            self._prepared_question = None  # clear for next call
            try:
                answer = round(float(a)) if a is not None else None
            except (TypeError, ValueError):
                answer = None
            return q, answer
            
        self.process_file()
        return self.get_random_question()


    def process_file(self):
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
        
        if isinstance(self.difficultyIndex, list):
             valid_difficulties = self.difficultyIndex
        else:
             valid_difficulties = [self.difficultyIndex]

        self.df = self.df[
        (self.df["type"] == self.questionType.lower().strip()) &
        (self.df["difficulty"].isin(valid_difficulties))]

        self.df = self.df.sort_values(by="difficulty", ascending=True)

    def quickplay(self):
        self.process_for_quickplay()
        return self.get_random_question()

    def process_for_quickplay(self):
        file_path = os.path.join(os.getcwd(), "question", "question.xlsx")
        print(f"[QuickPlay] Reloading file fresh: {file_path}")

        df = pd.read_excel(file_path)
        df = pd.DataFrame(df)

        df["type"] = df["type"].astype(str).str.strip().str.lower()
        df["difficulty"] = pd.to_numeric(df["difficulty"], errors="coerce")

        if isinstance(self.difficultyIndex, list):
             valid_difficulties = self.difficultyIndex
        else:
             valid_difficulties = [self.difficultyIndex]

        df = df[df["difficulty"].isin(valid_difficulties)]

        if df.empty:
            print(f"[QuickPlay] No questions found at difficulty {self.difficultyIndex}")
        else:
            print(f"[QuickPlay] {len(df)} questions found at difficulty {self.difficultyIndex}")

        df = df.sample(frac=1).reset_index(drop=True)
        self.df = df

    def get_random_question(self):
        if self.df is None or self.df.empty:
            return "No questions found.", None
 
        self.rowIndex = random.randint(0, len(self.df) - 1)
 
        variable_string = str(self.df.iloc[self.rowIndex]["operands"])


        input_string = ''.join(c for c in variable_string if not c.isalpha())
        self.variables = [c for c in variable_string if c.isalpha()]
        self.oprands = self.parseInputRange(input_string)
 
        # ✅ DYNAMIC LANGUAGE SELECTION USING YOUR EXCEL FILE
        current_lang = getattr(lang_config, 'selected_language', 'English')
        
        if current_lang == "हिंदी" and "question_hi" in self.df.columns:
            question_template = str(self.df.iloc[self.rowIndex]["question_hi"])
        elif current_lang == "മലയാളം" and "question_mal" in self.df.columns:
            question_template = str(self.df.iloc[self.rowIndex]["question_mal"])
        else:
            # Otherwise default to the English 'question' column
            question_template = str(self.df.iloc[self.rowIndex]["question"])

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
        final_answer = self.solveEquation(answer_equation)
        self.Pr_answer = str(final_answer)
 
    def getAnswer(self, row, column):
        ans_equation = str(self.df.iloc[row][column])
        ans_equation = ans_equation.replace("×", "*")  
        for i in range(len(self.variables)):
            ans_equation = ans_equation.replace(f"{{{self.variables[i]}}}", str(self.oprands[i]))
        return ans_equation

    def solveEquation(self, ans_equation):
        try:
            return eval(ans_equation)
        except Exception as e:
            return None
 
    def removeVariables(self, row, column):
        val = self.df.iloc[row, column]
        return ''.join(c for c in val if not c.isalpha())
 
    def allVariables(self, row, column):
        val = self.df.iloc[row, column]
        return [c for c in val if c.isalpha()]

    def parseInputRange(self, inputRange):
        operands = []
        current = ""
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
            elif ":" in inputRange:
                a, b = map(int, inputRange.split(":"))
                return random.randint(a, b)
            elif ";" in inputRange:
                a, b, c = map(int, inputRange.split(";"))
                return a * random.randint(b, c)
            return int(inputRange)
        except Exception as e:
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
            user_val = float(user_answer)
            correct_val = float(correct_answer)
        except (ValueError, TypeError):
            return {"valid": False}
        
        self.total_attempts += 1
        is_correct = user_val == correct_val
    
        if is_correct:
            self.correct_answers += 1
            self.correct_streak += 1
            self.incorrect_streak = 0
            self.current_performance_rate += 5  
            if time_taken < 5:
                self.current_performance_rate += 5
            elif time_taken < 10:
                self.current_performance_rate += 2
        else:
            self.incorrect_streak += 1
            self.correct_streak = 0
            self.current_performance_rate -= 10  
            if time_taken > 15:
                self.current_performance_rate -= 5 
 
        if isinstance(self.current_difficulty, list):
            return {"valid": True, "correct": is_correct}

        if self.current_performance_rate >= 30:
            if self.current_difficulty < 5:  
                self.current_difficulty += 1
                self.difficultyIndex = self.current_difficulty
            self.current_performance_rate = 0
 
        elif self.current_performance_rate <= -30:
            if self.current_difficulty > 1:
                self.current_difficulty -= 1
            self.current_performance_rate = 0
        
        return {
        "valid": True,
        "correct": is_correct
    }

class GameSession:
    TIER1 = ["Addition", "Subtraction", "Multiplication", "Division", "Remainder", "Percentage"]
    TIER2 = ["Story", "Time", "Currency", "Distance", "Bellring"]
    MAX_QUESTIONS = 20

    def __init__(self, difficulty_index):
        self.difficulty_index = difficulty_index
        self.difficulty = difficulty_index
        self.skill_scores = {skill: 50 for skill in self.TIER1}
        self.correct_streak = 0
        self.incorrect_streak = 0
        self.state = "Normal"  # "Normal" | "Thriving" | "Struggling"
        self.mistake_queue = []  # list of dict: {'skill_type': ..., 'resurfaced_at': ...}
        self.question_count = 0
        self.questions_answered = 0
        self.phase = "Warmup"  # "Warmup" | "Main" | "Finale"
        self.tier2_index = 0
        self.current_skill = None
        self.recent_performance = []
        self.session_time = 90
        
        # Deduplication
        self.used_question_indices = {}
        self.used_question_texts = set()


    def is_session_complete(self):
        return self.question_count >= self.MAX_QUESTIONS

    def set_finale(self):
        self.phase = "Finale"

    def get_phase(self):
        return self.phase

    def get_next_question(self):
        skill = None

        if self.question_count >= 19:
            self.phase = "Finale"

        if self.phase == "Finale":
            skill = max(self.skill_scores, key=self.skill_scores.get)
        elif self.phase == "Warmup" and self.question_count < 3:
            scores = list(self.skill_scores.values())
            if all(s == scores[0] for s in scores):
                # Avoid Multiplication/Division on absolute first question for warmups
                safe_warmup = [s for s in self.TIER1 if s not in ["Multiplication", "Division"]]
                skill = random.choice(safe_warmup)
            else:
                skill = max(self.skill_scores, key=self.skill_scores.get)

        else:
            self.phase = "Main"
            if self.question_count % 5 == 0 and self.question_count > 0:
                skill = self.TIER2[self.tier2_index % len(self.TIER2)]
                self.tier2_index += 1
            else:
                for item in list(self.mistake_queue):
                    if item['resurfaced_at'] <= self.question_count:
                        skill = item['skill_type']
                        self.mistake_queue.remove(item)
                        break
                
                if not skill:
                    weights = self._get_weights_for_state(self.state)
                    roll = random.random()
                    
                    if roll < weights["weakness"]:
                        skill = min(self.skill_scores, key=self.skill_scores.get)
                    elif roll < weights["weakness"] + weights["strength"]:
                        skill = max(self.skill_scores, key=self.skill_scores.get)
                    else:
                        skill = random.choice(self.TIER1)

        self.current_skill = skill
        self.question_count += 1
        processor = QuestionProcessor(skill, self.difficulty)
        processor.process_file() 

        if hasattr(processor, 'df') and processor.df is not None and not processor.df.empty:
            used = self.used_question_indices.get(skill, set())
            available = [i for i in range(len(processor.df)) if i not in used]

            if not available:
                print(f"[GAME] All questions used for {skill}, resetting pool")
                self.used_question_indices[skill] = set()
                available = list(range(len(processor.df)))

            chosen_row = None
            translated_template = None

            # Retry loop to avoid text duplicates
            while available:
                row_index = random.choice(available)
                available.remove(row_index)

                processor.rowIndex = row_index
                variable_string = str(processor.df.iloc[row_index]["operands"])
                input_string = ''.join(c for c in variable_string if not c.isalpha())
                processor.variables = [c for c in variable_string if c.isalpha()]
                processor.oprands = processor.parseInputRange(input_string)
                processor.extractAnswer()

                import language.language as lang_config
                current_lang = getattr(lang_config, 'selected_language', 'English')

                template = "No question template found"
                if current_lang == "हिंदी" and "question_hi" in processor.df.columns:
                    template = str(processor.df.iloc[row_index]["question_hi"])
                elif current_lang == "മലയാളം" and "question_mal" in processor.df.columns:
                    template = str(processor.df.iloc[row_index]["question_mal"])
                elif current_lang == "தமிழ்" and "question_tam" in processor.df.columns:
                    template = str(processor.df.iloc[row_index]["question_tam"])
                else:
                    template = str(processor.df.iloc[row_index]["question"])

                # Replacements
                for i, var in enumerate(processor.variables):
                    template = template.replace(f"{{{var}}}", str(processor.oprands[i]))

                if template not in self.used_question_texts or not available:
                    chosen_row = row_index
                    translated_template = template
                    break

            if chosen_row is not None:
                processor.rowIndex = chosen_row
                self.used_question_indices.setdefault(skill, set()).add(chosen_row)
                self.used_question_texts.add(translated_template)
                processor._prepared_question = translated_template
                processor._prepared_answer = processor.Pr_answer
                print(f"[GAME] Skill: {skill} | Row: {chosen_row} | Q: '{translated_template}'")

        return processor



    def _get_weights_for_state(self, state):
        if state == "Struggling":
            return {"weakness": 0.10, "strength": 0.60, "novelty": 0.30}
        elif state == "Thriving":
            return {"weakness": 0.65, "strength": 0.10, "novelty": 0.25}
        else: # Normal
            return {"weakness": 0.45, "strength": 0.20, "novelty": 0.35}

    def submit_answer(self, skill_type, is_correct, elapsed):
        delta = 0
        self.questions_answered += 1
        if is_correct:
            self.correct_streak += 1
            self.incorrect_streak = 0
            if elapsed < 5:
                delta = 8
                perf = "excellent"
            elif elapsed < 10:
                delta = 5
                perf = "good"
            elif elapsed < 15:
                delta = 3
                perf = "fair"
            else:
                delta = 1
                perf = "slow"
            self.recent_performance.append(perf)
        else:
            self.incorrect_streak += 1
            self.correct_streak = 0
            if self.incorrect_streak == 1:
                delta = -5
            else:
                delta = -8
            if len(self.mistake_queue) < 2:
                self.mistake_queue.append({'skill_type': skill_type, 'resurfaced_at': self.question_count + 3})
            self.recent_performance.append("incorrect")

        if skill_type in self.skill_scores:
            self.skill_scores[skill_type] = max(0, min(100, self.skill_scores[skill_type] + delta))

        # State machine
        if self.incorrect_streak >= 2:
            self.state = "Struggling"
        elif self.correct_streak >= 3:
            if len(self.recent_performance) >= 3 and all(p == "excellent" for p in self.recent_performance[-3:]):
                self.state = "Thriving"
        elif self.state == "Struggling" and is_correct:
            self.state = "Normal"
        elif self.state == "Thriving" and not is_correct:
            self.state = "Normal"

        if len(self.recent_performance) > 10:
            self.recent_performance = self.recent_performance[-10:]

    def generate_report(self):
        ranked = sorted(self.skill_scores.items(), key=lambda x: x[1], reverse=True)
        strengths = [s for s, score in ranked if score >= 60][:2]
        weakness = [s for s, score in ranked if score < 45][:1]

        from language.language import tr

        if strengths:
            s1 = tr(strengths[0])
            s2 = tr(strengths[1]) if len(strengths) > 1 else None
            strength_text = f"{s1} {tr('and')} {s2}" if s2 else s1
        else:
            strength_text = tr("trying hard")

        if weakness:
             weak_name = tr(weakness[0])
             endings = [
                 tr("{skill} is your next adventure!").format(skill=weak_name),
                 tr("Keep exploring {skill}!").format(skill=weak_name),
                 tr("{skill} wants more of your attention!").format(skill=weak_name)
             ]
             weak_sentence = random.choice(endings)
        else:
             weak_sentence = tr("You are brilliant across everything!")

        templates = [
             tr("You were amazing at {strength} today! {weakness}").format(
                 strength=strength_text, weakness=weak_sentence),
             tr("Wow! {strength} is your superpower. {weakness}").format(
                 strength=strength_text, weakness=weak_sentence),
             tr("Great session! You really know your {strength}. {weakness}").format(
                 strength=strength_text, weakness=weak_sentence)
        ]
        return random.choice(templates)

