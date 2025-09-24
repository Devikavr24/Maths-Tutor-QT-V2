import os
import pandas as pd
import random


class QuestionProcessor:
    def __init__(self, questionType):
        self.questionType = questionType
        self.df = None
        self.variables = []
        self.oprands = []
        self.rowIndex = 0

    def process_file(self):
        file_path = os.path.join(os.getcwd(), "question", "question.xlsx")
        self.df = pd.read_excel(file_path)
        self.df = self.df[self.df["type"] == self.questionType]
        self.df = self.df.reset_index(drop=True)
        

    def get_random_question(self):
        if self.df.empty:
            return "No questions found."

        self.rowIndex = random.randint(0, len(self.df) - 1)
        self.variables = self.allVariables(self.rowIndex, 2)
        inputRange = self.removeVariables(self.rowIndex, 2)
        self.parseInputRange(inputRange)
        return self.replaceVariables(self.rowIndex, 0)

    def removeVariables(self, row, column):
        val = self.df.iloc[row, column]
        return ''.join(c for c in val if not c.isalpha())

    def allVariables(self, row, column):
        val = self.df.iloc[row, column]
        return [c for c in val if c.isalpha()]

    def parseInputRange(self, inputRange):
        self.oprands = []
        current = ""
        for c in inputRange:
            if c == "*":
                self.oprands.append(int(self.extractType(current)))
                current = ""
            else:
                current += c
        if current:
            self.oprands.append(int(self.extractType(current)))

    def extractType(self, inputRange):
        if "," in inputRange:
            return random.choice(list(map(int, inputRange.split(","))))
        elif ":" in inputRange:
            a, b = map(int, inputRange.split(":"))
            return random.randint(a, b)
        elif ";" in inputRange:
            a, b, c = map(int, inputRange.split(";"))
            return a * random.randint(b, c)
        return int(inputRange)

    def replaceVariables(self, row, column):
        val = self.df.iloc[row, column]
        for i, var in enumerate(self.variables):
            val = val.replace(f"{{{var}}}", str(self.oprands[i]))
        return val
