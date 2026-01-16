import pyttsx3
from PyQt5.QtCore import QObject, pyqtSignal, QThread, QTimer, QMutex

class TTSWorker(QObject):
    finished = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.engine = None
        self.timer = None
        self.iterating_lock = QMutex()

    def init_engine(self):
        """Initializes the engine and a timer to drive its event loop."""
        if not self.engine:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 150)
            self.timer = QTimer()
            self.timer.timeout.connect(self.iterate_loop)
            self.timer.start(100)

    def speak(self, text):
        """Speaks text using a non-blocking loop."""
        self.init_engine()
        
        # Ensure the timer is running, as it might have been stopped
        # by a previously completed announcement.
        if not self.timer.isActive():
            self.timer.start(100)
        
        # End any previous loop cleanly before starting a new one.
        if self.engine._inLoop:
            try:
                self.engine.endLoop()
            except RuntimeError:
                # This can happen in rare cases. Re-initializing is the safest recovery.
                self.reset()
                self.init_engine()

        self.engine.say(text)
        self.engine.startLoop(False)

    def iterate_loop(self):
        """Periodically drives the pyttsx3 event loop, protected by a mutex."""
        if self.iterating_lock.tryLock():
            try:
                if self.engine and self.engine._inLoop:
                    self.engine.iterate()
                elif self.timer:
                    # Stop the timer if the loop has ended to save resources.
                    self.timer.stop()
            finally:
                self.iterating_lock.unlock()

    def stop(self):
        """Stops the current utterance and ends the event loop."""
        if self.engine:
            if self.engine.isBusy():
                self.engine.stop()
            if self.engine._inLoop:
                self.engine.endLoop()

    def reset(self):
        """Destroys the current engine and timer to allow for a fresh start."""
        if self.timer:
            self.timer.stop()
        self.engine = None
        self.timer = None

    def cleanup(self):
        """Safely stops the timer from the worker thread before quitting."""
        if self.timer:
            self.timer.stop()


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