# tts_engine.py
import pyttsx3

engine = pyttsx3.init(driverName='espeak')
engine.setProperty('rate', 150)
engine.setProperty('volume', 1.0)
