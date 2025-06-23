# tts.py
import pyttsx3

class TextToSpeech:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        self.engine.setProperty('volume', 1.0)

    def speak(self, text):
        if text:
            self.engine.say(text)
            self.engine.runAndWait()