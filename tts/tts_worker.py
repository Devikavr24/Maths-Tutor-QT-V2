import platform
import subprocess
from PyQt5.QtCore import QObject, pyqtSignal, QThread, QTimer, QMutex

import language.language as lang_config

if platform.system() == "Windows":
    import pyttsx3
    import win32com.client
    import pythoncom

class TTSWorker(QObject):
    finished = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.system = platform.system()
        self.process = None  # Used for espeak-ng on Linux AND as fallback on Windows
        if self.system == "Windows":
            self.engine = None
            self.timer = None
            self.iterating_lock = QMutex()
            self.sapi = None  # Dedicated engine for Windows Modern (OneCore) voices

    def speak(self, text):
        current_lang = getattr(lang_config, 'selected_language', 'English')
        
        # ✅ FIX: Convert standard numbers to Hindi Devanagari numerals for correct pronunciation
        if current_lang == "हिंदी":
            hindi_numerals = {
                '0': '०', '1': '१', '2': '२', '3': '३', '4': '४', 
                '5': '५', '6': '६', '7': '७', '8': '८', '9': '९'
            }
            for eng_num, hin_num in hindi_numerals.items():
                text = text.replace(eng_num, hin_num)

        if self.system == "Windows":
            self._speak_windows(text, current_lang)
        else:
            self._speak_linux(text, current_lang)

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
            self.sapi = None

    # --- Windows Methods ---
    def _init_windows_engine(self):
        if not self.engine:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 150)
            self.timer = QTimer(self)
            self.timer.timeout.connect(self._iterate_windows_loop)
            self.timer.start(100)

    def _speak_windows(self, text, current_lang):
        self._stop_windows() # Stop any previous speech

        # 1. ATTEMPT NATIVE HINDI (OneCore) OR FALLBACK TO ESPEAK-NG
        if current_lang == "हिंदी":
            hindi_voice_found = False
            try:
                pythoncom.CoInitialize() # Required for COM in QThread
                if not self.sapi:
                    self.sapi = win32com.client.Dispatch("SAPI.SpVoice")
                
                # Tell SAPI to look in the Modern OneCore registry path
                cat = win32com.client.Dispatch("SAPI.SpObjectTokenCategory")
                cat.SetId(r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech_OneCore\Voices", False)
                
                hindi_voice = None
                for token in cat.EnumerateTokens():
                    desc = token.GetDescription().lower()
                    if "hindi" in desc or "kalpana" in desc or "hemant" in desc:
                        hindi_voice = token
                        hindi_voice_found = True
                        break
                
                if hindi_voice_found and hindi_voice:
                    self.sapi.Voice = hindi_voice
                    self.sapi.Speak(text, 1) # 1 = Speak Asynchronously
                    return  # Success! Skip the rest.
            except Exception as e:
                print("Native Windows Hindi check failed:", e)

            # 2. ESPEAK-NG FALLBACK (If Native Hindi fails or isn't installed)
            if not hindi_voice_found:
                print("Windows Hindi pack not found. Falling back to espeak-ng...")
                try:
                    # 0x08000000 = CREATE_NO_WINDOW (Hides the ugly terminal popup on Windows)
                    flags = 0x08000000 
                    self.process = subprocess.Popen(['espeak-ng', '-v', 'hi', text], creationflags=flags)
                    return
                except FileNotFoundError:
                    print("🚨 [TTS ERROR] espeak-ng is not installed or added to system PATH.")
                    return

        # 3. STANDARD ENGLISH / DEFAULT PYTTSX3 LOGIC
        self._init_windows_engine()
        voices = self.engine.getProperty('voices')
        
        target_voice = None
        for voice in voices:
            v_name = voice.name.lower()
            v_id = voice.id.lower()
            if current_lang != "हिंदी" and ("english" in v_name or "en-us" in v_id or "zira" in v_name or "david" in v_name):
                target_voice = voice.id
                break
                
        if target_voice:
            self.engine.setProperty('voice', target_voice)

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
                pass
            finally:
                self.iterating_lock.unlock()

    def _stop_windows(self):
        # Stop OneCore SAPI if active
        if hasattr(self, 'sapi') and self.sapi:
            try:
                self.sapi.Speak("", 3) # 3 = Async + PurgeBeforeSpeak
            except:
                pass

        # Stop pyttsx3 if active
        if self.engine and self.engine.isBusy():
            self.engine.stop()
            
        # Stop espeak-ng fallback if active
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=0.1)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.process = None

    def _cleanup_windows(self):
        if self.timer:
            self.timer.stop()
        if self.engine and self.engine._inLoop:
            try:
                self.engine.endLoop()
            except RuntimeError:
                pass
        self.engine = None
        self.sapi = None
        self._stop_windows()

    # --- Linux Methods ---
    def _speak_linux(self, text, current_lang):
        self._stop_linux()
        try:
            voice_arg = 'hi' if current_lang == "हिंदी" else 'en'
            self.process = subprocess.Popen(['espeak-ng', '-v', voice_arg, text])
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