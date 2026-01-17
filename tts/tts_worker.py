import platform
import subprocess
from PyQt5.QtCore import QObject, pyqtSignal, QThread

if platform.system() == "Windows":
    import pyttsx3

class TTSWorker(QObject):
    finished = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        if platform.system() == "Windows":
            self.engine = None
        else:
            self.process = None

    def speak(self, text):
        """Speaks text using the appropriate TTS engine for the OS."""
        if platform.system() == "Windows":
            self._speak_windows(text)
        else:
            self._speak_linux(text)

    def _speak_windows(self, text):
        if not self.engine:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 150)
        
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"TTS Error (Windows): {e}")

    def _speak_linux(self, text):
        """Speaks text using the espeak-ng command-line tool."""
        if self.process and self.process.poll() is None:
            self.process.terminate()
            self.process.wait()

        try:
            self.process = subprocess.Popen(['espeak-ng', text])
        except FileNotFoundError:
            print("espeak-ng not found. Please install it.")
        except Exception as e:
            print(f"An unexpected TTS Error occurred (Linux): {e}")

    def stop(self):
        """Stops the current utterance."""
        if platform.system() == "Windows":
            if self.engine:
                self.engine.stop()
        else:
            if self.process and self.process.poll() is None:
                self.process.terminate()
                try:
                    self.process.wait(timeout=0.1)
                except subprocess.TimeoutExpired:
                    self.process.kill()
            self.process = None

    def reset(self):
        self.stop()

    def cleanup(self):
        self.stop()


class TextToSpeech(QObject):
    speak_signal = pyqtSignal(str)
    stop_signal = pyqtSignal()
    reset_signal = pyqtSignal()
    cleanup_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.thread = QThread()
        self.worker = TTSWorker()
        self.worker.moveToThread(self.thread)
        
        self.speak_signal.connect(self.worker.speak)
        self.stop_signal.connect(self.worker.stop)
        self.reset_signal.connect(self.worker.reset)
        self.cleanup_signal.connect(self.worker.cleanup)
        
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def speak(self, text):
        self.speak_signal.emit(text)

    def stop(self):
        self.stop_signal.emit()
        
    def reset(self):
        self.reset_signal.emit()

    def cleanup(self):
        self.cleanup_signal.emit()
        self.thread.quit()
        self.thread.wait()
