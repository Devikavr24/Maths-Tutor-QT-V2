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
    play_custom_sound = pyqtSignal(str) # 👈 Signal to trigger play_sound in MainThread
    
    def __init__(self):
        super().__init__()
        self.system = platform.system()
        self.process = None  # Used for espeak-ng on Linux AND as fallback on Windows
        if self.system == "Windows":
            self.engine = None
            self.sapi = None  # Dedicated engine for Windows Modern (OneCore) voices
        self.iterating_lock = QMutex()
        self.speech_rate = 150  # Default WPM
        self.DEFAULT_RATE = 150
        self.RATE_STEP = 25

    @property
    def is_speaking(self):
        if self.system == "Windows":
            busy = False
            if self.engine:
                try:
                    busy = self.engine.isBusy()
                except Exception:
                    pass
            # SAPI doesn't have a simple isBusy, but if sapi exists we assume it might be speaking
            return busy
        else:
            return self.process is not None and self.process.poll() is None

    def set_rate(self, rate):
        # Clip rate between 50 and 300
        self.speech_rate = max(50, min(300, rate))
        
        if self.system == "Windows":
            if self.engine:
                try:
                    self.engine.setProperty('rate', self.speech_rate)
                except Exception:
                    pass
            if self.sapi:
                try:
                    # SAPI rate is from -10 to 10. Map 150 -> 0, 50 -> -10, 300 -> 10
                    sapi_rate = int((self.speech_rate - 150) / 15)
                    self.sapi.Rate = max(-10, min(10, sapi_rate))
                except Exception:
                    pass

    def speak(self, text):
        current_lang = getattr(lang_config, 'selected_language', 'en')
        
        # Convert standard numbers to regional script numerals for correct native pronunciation
        text = lang_config.localize_numbers(text)

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
            self.sapi = None

    # --- Windows Methods ---
    def _init_windows_engine(self):
        if not self.engine:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', self.speech_rate)

    def _speak_windows(self, text, current_lang):
        self._stop_windows() # Stop any previous speech

                # 1. ATTEMPT NATIVE VOICE (OneCore) OR FALLBACK TO ESPEAK-NG
                # Expanded target validation container supporting your full array of regional locale requirements
        target_languages = ["hi_IN", "ml_IN", "mr_IN", "ta_IN", "sa_IN", "ar_SA"]

        if current_lang in target_languages:
            voice_found = False
            
            # 1. Define Language Engine Map Profiles (Language Code, Display Name, Native Token Targets)
            lang_profiles = {
                "hi_IN": {"code": "hi", "search": "hindi",      "tokens": ["kalpana", "hemant"]},
                "ml_IN": {"code": "ml", "search": "malayalam",   "tokens": ["midhun", "sobhana"]},
                "mr_IN": {"code": "mr", "search": "marathi",    "tokens": ["hemant", "kalpana"]}, # Shares phonetic base engines
                "ta_IN": {"code": "ta", "search": "tamil",      "tokens": ["valluvar", "vani"]},
                "sa_IN": {"code": "sa", "search": "sanskrit",   "tokens": ["hemant", "laxmi"]},
                "ar_SA": {"code": "ar", "search": "arabic",     "tokens": ["naayf", "hoda"]}      # Universal Arabic standard profile
            }
            
            # Extract structural profile config values based on current active runtime string
            profile = lang_profiles[current_lang]
            lang_code = profile["code"]
            search_name = profile["search"]
            target_tokens = profile["tokens"]
            
            try:
                pythoncom.CoInitialize() # Required for COM bindings in explicit multi-threaded pipelines (QThread)
                if not self.sapi:
                    self.sapi = win32com.client.Dispatch("SAPI.SpVoice")
                
                # Point SAPI lookup context directly to the high-quality Modern Windows OneCore directory space
                cat = win32com.client.Dispatch("SAPI.SpObjectTokenCategory")
                cat.SetId(r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech_OneCore\Voices", False)
                
                target_voice = None
                for token in cat.EnumerateTokens():
                    desc = token.GetDescription().lower()
                    
                    # Match via primary display string configuration or fallback internal engine name profiles
                    is_name_match = search_name in desc
                    is_token_match = any(token_name in desc for token_name in target_tokens)

                    if is_name_match or is_token_match:
                        target_voice = token
                        voice_found = True
                        break

                if voice_found and target_voice:
                    self.sapi.Voice = target_voice
                    self.set_rate(self.speech_rate)
                    self.sapi.Speak(text, 1) # Execution parameter 1 = Speak Asynchronously without locking UI
                    return  # Exit tracking execution context on successful native playback route
                    
            except Exception as e:
                print(f"Native Windows OneCore {search_name} check failed:", e)

            # 2. SEAMLESS MULTI-FALLBACK CROSS-COMPATIBILITY PIPELINE (Triggered if native assets missing)
            if not voice_found:
                print(f"Windows {current_lang} structural asset engine missing. Initializing fallback platform...")
                try:
                    import shutil, os, subprocess
                    espeak_exe = shutil.which('espeak-ng') or shutil.which('espeak')
                    
                    if not espeak_exe:
                        # Array of standard path locations for classical x86 windows builds
                        fallback_locations = [
                            r"C:\Program Files (x86)\eSpeak\command_line\espeak.exe",
                            r"C:\Program Files (x86)\eSpeak\espeak.exe",
                            r"C:\Program Files\eSpeak NG\espeak-ng.exe"
                        ]
                        for path in fallback_locations:
                            if os.path.exists(path):
                                espeak_exe = path
                                break

                    if not espeak_exe:
                        print(f"🚨 [TTS ERROR] Unable to locate local eSpeak tools for execution fallback pipeline setup.")
                        return

                    # Explicit execution window safety flags to intercept popping command prompt windows
                    flags = 0x08000000 # CREATE_NO_WINDOW 
                    
                    # Deploy process argument profile mappings context
                    self.process = subprocess.Popen(
                        [espeak_exe, '-v', f"{lang_code}+f3", '--stdin'],
                        stdin=subprocess.PIPE,
                        creationflags=flags
                    )
                    
                    # Append newline boundary token so the audio queue process synthesises chunks directly without buffer lockup
                    formatted_text = text + "\n"
                    self.process.stdin.write(formatted_text.encode('utf-8'))
                    self.process.stdin.flush()
                    self.process.stdin.close()
                    return
                    
                except Exception as e:
                    print(f"🚨 [TTS ERROR] Fatal failure during cross-platform fallback processing sequence: {e}")
                    return

        # 3. STANDARD ENGLISH / DEFAULT PYTTSX3 LOGIC
        self._init_windows_engine()
        voices = self.engine.getProperty('voices')
        
        target_voice = None
        for voice in voices:
            v_name = voice.name.lower()
            v_id = voice.id.lower()
            if current_lang != "hi_IN" and ("english" in v_name or "en-us" in v_id or "zira" in v_name or "david" in v_name):
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
            if current_lang == "hi_IN": voice_arg = 'hi'
            elif current_lang == "ml_IN": voice_arg = 'ml'
            else: voice_arg = 'en'
            
            self.process = subprocess.Popen(['espeak-ng', '-v', voice_arg, '-s', str(self.speech_rate), text])
        except FileNotFoundError:
            try:
                # Fallback to spd-say if espeak-ng is not found
                speed = int((self.speech_rate - 150) / 1.5) # spd-say rate is -100 to 100
                speed = max(-100, min(100, speed))
                self.process = subprocess.Popen(['spd-say', '-l', voice_arg, '-r', str(speed), text])
            except FileNotFoundError:
                print("espeak-ng and spd-say not found. Please install one of them.")
            except Exception as e:
                print(f"An unexpected TTS Error occurred (Linux Fallback): {e}")
        except Exception as e:
            print(f"An unexpected TTS Error occurred (Linux): {e}")
        
    def _iterate_linux_loop(self):
        if self.iterating_lock.tryLock():
            try:
                if self.process:
                    status = self.process.poll()
                    if status is not None:
                        self.process = None
            except (RuntimeError, TypeError):
                pass
            finally:
                self.iterating_lock.unlock()

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
    play_custom_sound_signal = pyqtSignal(str) # 👈 Forward Signal
    stop_signal = pyqtSignal()
    reset_signal = pyqtSignal()
    cleanup_signal = pyqtSignal()
    set_rate_signal = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.thread = QThread()
        self.worker = TTSWorker()
        self.worker.moveToThread(self.thread)
        
        # Safe main-thread timer initialization
        self.iterate_timer = QTimer()
        if self.worker.system == "Windows" : self.iterate_timer.timeout.connect(self.worker._iterate_windows_loop)
        elif self.worker.system == "Linux" : self.iterate_timer.timeout.connect(self.worker._iterate_linux_loop)
        self.iterate_timer.start(100)
        
        self.speak_signal.connect(self.worker.speak)
        self.worker.play_custom_sound.connect(self.play_custom_sound_signal.emit) # 👈 Connect forward
        self.stop_signal.connect(self.worker.stop)
        self.reset_signal.connect(self.worker.reset)
        self.cleanup_signal.connect(self.worker.cleanup)
        self.set_rate_signal.connect(self.worker.set_rate)
        
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def speak(self, text):
        self.speak_signal.emit(text)

    def stop(self):
        self.stop_signal.emit()
        
    def reset(self):
        self.reset_signal.emit()

    def cleanup(self):
        if hasattr(self, 'iterate_timer'):
            self.iterate_timer.stop()
            self.iterate_timer.deleteLater()
            
        self.cleanup_signal.emit()
        self.thread.quit()
        self.thread.wait()
        
    def set_rate(self, rate):
        self.set_rate_signal.emit(rate)
        
    @property
    def speech_rate(self):
        return self.worker.speech_rate
    
    @property
    def is_speaking(self):
        return self.worker.is_speaking
    
    @property
    def DEFAULT_RATE(self):
        return self.worker.DEFAULT_RATE
    
    @property
    def RATE_STEP(self):
        return self.worker.RATE_STEP