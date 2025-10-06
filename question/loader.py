import os
import pandas as pd
import random







class QuestionProcessor:
    def __init__(self, questionType,difficultyIndex):
        self.questionType = questionType
        self.widget = None
        self.difficultyIndex = difficultyIndex
        self.df = None
        self.variables = []
        self.oprands = []
        self.rowIndex = 0
        self.retry_count = 0
         # ✅ DDA-related fields
        self.total_attempts = 0
        self.correct_answers = 0
        self.correct_streak = 0
        self.incorrect_streak = 0
        self.current_performance_rate = 0
        self.current_difficulty = difficultyIndex  # Use to adjust difficulty dynamically
    def get_questions(self):
        
        self.process_file()
        return self.get_random_question()
    def process_file(self):
        file_path = os.path.join(os.getcwd(), "question", "question.xlsx")
        print(f"Processing file: {file_path}")

        
        self.df = pd.read_excel(file_path)

        self.df = pd.DataFrame(self.df)
        

        # # If you are using "type" column as the section filter:
        # if "type" in self.df.columns:
        #     print("[INFO] Available sections (from 'type'):", self.df["type"].unique().tolist())

        # # If you are using "section" column:
        # elif "section" in self.df.columns:
        #     print("[INFO] Available sections (from 'section'):", self.df["section"].unique().tolist())
        # else:
        #     print("[WARNING] No 'section' or 'type' column found in question file")

        if self.questionType == "custom":
            print("[Processor] Custom uploaded file detected — skipping filtering.")
            return

        # Normalize
        #self.df["type"] = self.df["type"].astype(str)
        self.df["difficulty"] = pd.to_numeric(self.df["difficulty"], errors="coerce")
        self.df["type"] = self.df["type"].astype(str).str.strip().str.lower()

        print(f"[Processor] Filtering with section: {self.questionType}")
        
        # # Define difficulty levels to include
        if isinstance(self.difficultyIndex, list):
             valid_difficulties = self.difficultyIndex
        else:
             valid_difficulties = [self.difficultyIndex]
        print("[DEBUG] Unique types in Excel:", self.df["type"].unique())
        print("[DEBUG] Unique difficulties in Excel:", self.df["difficulty"].unique())
        print("[DEBUG] Target type:", self.questionType)
        print("[DEBUG] Target difficulties:", valid_difficulties)

        self.df = self.df[
        (self.df["type"] == self.questionType.lower().strip()) &
        (self.df["difficulty"].isin(valid_difficulties))]

        self.df = self.df.sort_values(by="difficulty", ascending=True)
        print(self.df.head())  # Debug

    def quickplay(self):
        self.process_for_quickplay()
        return self.get_random_question()
    def process_for_quickplay(self):
        file_path = os.path.join(os.getcwd(), "question", "question.xlsx")
        print(f"[QuickPlay] Reloading file fresh: {file_path}")

        df = pd.read_excel(file_path)
        df = pd.DataFrame(df)

        # Normalize
        df["type"] = df["type"].astype(str).str.strip().str.lower()
        df["difficulty"] = pd.to_numeric(df["difficulty"], errors="coerce")

        print("[QuickPlay] Unique types in Excel:", df["type"].unique())
        print("[QuickPlay] Unique difficulties in Excel:", df["difficulty"].unique())

        # Filter only by difficulty
        df = df[df["difficulty"] == self.difficultyIndex]

        if df.empty:
            print(f"[QuickPlay] No questions found at difficulty {self.difficultyIndex}")
        else:
            print(f"[QuickPlay] {len(df)} questions found at difficulty {self.difficultyIndex}")

        # Randomize
        df = df.sample(frac=1).reset_index(drop=True)

        self.df = df

    def get_random_question(self):
        if self.df.empty:
            return "No questions found.", None
 
        self.rowIndex = random.randint(0, len(self.df) - 1)
 
        # Get variable names and operand ranges from the format column (col 2)
        #variable_string = str(self.df.iloc[self.rowIndex, 2])
        variable_string = str(self.df.iloc[self.rowIndex]["operands"])
        input_string = ''.join(c for c in variable_string if not c.isalpha())
        self.variables = [c for c in variable_string if c.isalpha()]
        self.oprands = self.parseInputRange(input_string)
 
        # Debug info
        print(f"[DEBUG] Variables: {self.variables}")
        print(f"[DEBUG] Operands: {self.oprands}")
 
        # Replace placeholders in the question string (col 0)
         #question_template = str(self.df.iloc[self.rowIndex, 0])
        question_template = str(self.df.iloc[self.rowIndex]["question"])
        for i, var in enumerate(self.variables):
            question_template = question_template.replace(f"{{{var}}}", str(self.oprands[i]))
 
        # Extract and solve answer using helper functions
        self.extractAnswer()
        try:
            #answer = int(float(self.Pr_answer))
            answer = round(float(self.Pr_answer)) if self.Pr_answer is not None else None
        except (TypeError, ValueError):
            print(f"[ERROR] Invalid answer: {self.Pr_answer}")
            answer = None
        #answer = int(self.Pr_answer) if self.Pr_answer is not None else None
        

 
        print(f"Question shown: {question_template}")
        print(f"Answer calculated: {answer}")
        return question_template, answer
    def extractAnswer(self):
        #answer_equation = self.getAnswer(self.rowIndex, 4)  # assuming column 4 contains the formula
        answer_equation = self.getAnswer(self.rowIndex, "equation")

        final_answer = self.solveEquation(answer_equation)
        print("finalAns:", final_answer)
        self.Pr_answer = str(final_answer)
 
    def getAnswer(self, row, column):
        ans_equation = str(self.df.iloc[row][column])
        ans_equation = ans_equation.replace("×", "*")  # ✅ replace invalid multiplication sign
        for i in range(len(self.variables)):
            ans_equation = ans_equation.replace(f"{{{self.variables[i]}}}", str(self.oprands[i]))
        print("ansEquation (parsed):", ans_equation)
        return ans_equation


 
    def solveEquation(self, ans_equation):
        try:
            return eval(ans_equation)
        except Exception as e:
            print("[ERROR] Evaluating equation:", e)
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
            print("[ERROR] Invalid inputRange format:", inputRange, e)
            return 0  # fallback

 
    def replaceVariables(self, rowIndex, columnIndex):
        val = str(self.df.iloc[rowIndex, columnIndex])  # Force string to allow .replace()
 
        for i, var in enumerate(self.variables):
            val = val.replace(f"{{{var}}}", str(self.oprands[i]))
 
        return val
 
   
    def submit_answer(self, user_answer, correct_answer, time_taken):
        self.total_attempts += 1
        is_correct = float(user_answer) == float(correct_answer)
 
        if is_correct:
            
            self.correct_answers += 1
            self.correct_streak += 1
            self.incorrect_streak = 0
 
            # ✅ Always reward for correct answer
            self.current_performance_rate += 5  # base reward
 
            # ⚡ Bonus for fast answers
            if time_taken < 5:
                self.current_performance_rate += 5
            elif time_taken < 10:
                self.current_performance_rate += 2
 
        else:
            
            self.incorrect_streak += 1
            self.correct_streak = 0
            self.current_performance_rate -= 10  # penalty for wrong answer
 
            if time_taken > 15:
                self.current_performance_rate -= 5  # extra penalty for hesitation
 
        # 🔐 Clamp difficulty changes to one level at a time
        if self.current_performance_rate >= 30:
            if self.current_difficulty < 5:  # max difficulty cap (optional)
                self.current_difficulty += 1
                self.difficultyIndex=self.current_difficulty
            self.current_performance_rate = 0
            print("🎯 Level up! Increased difficulty to", self.current_difficulty)
 
        elif self.current_performance_rate <= -30:
            if self.current_difficulty > 1:
                self.current_difficulty -= 1
            self.current_performance_rate = 0
            print("🔻 Level down. Decreased difficulty to", self.current_difficulty)
 
        # 📊 Feedback
        print(f"📊 Performance Rate: {self.current_performance_rate}")
        print(f"🎯 Current Difficulty: {self.current_difficulty}")
        print(f"📈 Attempts: {self.total_attempts} | Correct: {self.correct_answers}")