import platform
import subprocess
from PyQt5.QtCore import QObject, pyqtSignal, QThread, QTimer, QMutex

if platform.system() == "Windows":
    import pyttsx3

class TTSWorker(QObject):
    finished = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.system = platform.system()
        if self.system == "Windows":
            self.engine = None
            self.timer = None
            self.iterating_lock = QMutex()
        else: # Linux
            self.process = None

    def speak(self, text):
        if self.system == "Windows":
            self._speak_windows(text)
        else:
            self._speak_linux(text)

    def stop(self):
        if self.system == "Windows":
            self._stop_windows()
        else:
            self._stop_linux()

    def cleanup(self):
        if self.system == "Windows":
            self._cleanup_windows()
        else:
            self._cleanup_linux()
    
    def reset(self):
        self.cleanup()
        if self.system == "Windows":
            self.engine = None
            self.timer = None

    # --- Windows Methods ---
    def _init_windows_engine(self):
        if not self.engine:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 150)
            self.timer = QTimer(self)
            self.timer.timeout.connect(self._iterate_windows_loop)
            self.timer.start(100)

    def _speak_windows(self, text):
        self._init_windows_engine()
        self.engine.say(text)
        if not self.engine._inLoop:
            try:
                self.engine.startLoop(False)
            except RuntimeError:
                pass

    def _iterate_windows_loop(self):
        if self.iterating_lock.tryLock():
            try:
                if self.engine:
                    self.engine.iterate()
            except (RuntimeError, TypeError):
                # Seen on some systems when the loop is terminating
                pass
            finally:
                self.iterating_lock.unlock()

    def _stop_windows(self):
        if self.engine and self.engine.isBusy():
            self.engine.stop()

    def _cleanup_windows(self):
        if self.timer:
            self.timer.stop()
        if self.engine and self.engine._inLoop:
            try:
                self.engine.endLoop()
            except RuntimeError:
                pass
        self.engine = None

    # --- Linux Methods ---
    def _speak_linux(self, text):
        self._stop_linux() # Stop any previous speech
        try:
            # Use Popen to have control over the process
            self.process = subprocess.Popen(['espeak-ng', text])
        except FileNotFoundError:
            print("espeak-ng not found. Please install it.")
        except Exception as e:
            print(f"An unexpected TTS Error occurred (Linux): {e}")

    def _stop_linux(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=0.1)
            except subprocess.TimeoutExpired:
                self.process.kill()
        self.process = None
    
    def _cleanup_linux(self):
        self._stop_linux()


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
