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
            self.iterating_lock = QMutex()
            self.sapi = None  # Dedicated engine for Windows Modern (OneCore) voices
            
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
        current_lang = getattr(lang_config, 'selected_language', 'English')
        
        # Malayalam support
        if current_lang == "മലയാളം":
            import asyncio, edge_tts, os, uuid
            try:
                # Unique cache file
                cache_file = f"tts_cache_{uuid.uuid4().hex[:8]}.mp3"
                cache_path = os.path.join("sounds", cache_file)

                # Direct execution avoiding Subprocess interpreter latency
                communicate = edge_tts.Communicate(text, "ml-IN-SobhanaNeural")
                asyncio.run(communicate.save(cache_path))
                
                self.play_custom_sound.emit(cache_file)
                return # Skip standard fallback logic
            except Exception as e:
                print("[Edge TTS Error] Fallback failed:", e)
        
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
            self.sapi = None

    # --- Windows Methods ---
    def _init_windows_engine(self):
        if not self.engine:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', self.speech_rate)

    def _speak_windows(self, text, current_lang):
        self._stop_windows() # Stop any previous speech

        # 1. ATTEMPT NATIVE VOICE (OneCore) OR FALLBACK TO ESPEAK-NG
        if current_lang in ["हिंदी", "മലയാളം"]:
            voice_found = False
            lang_code = 'hi' if current_lang == "हिंदी" else 'ml'
            search_name = "hindi" if current_lang == "हिंदी" else "malayalam"
            
            try:
                pythoncom.CoInitialize() # Required for COM in QThread
                if not self.sapi:
                    self.sapi = win32com.client.Dispatch("SAPI.SpVoice")
                
                # Tell SAPI to look in the Modern OneCore registry path
                cat = win32com.client.Dispatch("SAPI.SpObjectTokenCategory")
                cat.SetId(r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech_OneCore\Voices", False)
                
                target_voice = None
                for token in cat.EnumerateTokens():
                    desc = token.GetDescription().lower()
                    if search_name in desc or (current_lang == "हिंदी" and ("kalpana" in desc or "hemant" in desc)):
                        target_voice = token
                        voice_found = True
                        break
                
                if voice_found and target_voice:
                    self.sapi.Voice = target_voice
                    # Map WPM to SAPI's -10 to 10 scale
                    sapi_rate = int((self.speech_rate - 150) / 15)
                    self.sapi.Rate = max(-10, min(10, sapi_rate))
                    self.sapi.Speak(text, 1) # 1 = Speak Asynchronously
                    return  # Success! Skip the rest.
            except Exception as e:
                print(f"Native Windows {search_name} check failed:", e)

            # 2. ESPEAK-NG FALLBACK (If Native fails or isn't installed)
            if not voice_found:
                print(f"Windows {current_lang} pack not found. Falling back to espeak-ng...")
                try:
                    import shutil, os
                    espeak_exe = shutil.which('espeak-ng')
                    if not espeak_exe:
                        fallback_path = r"C:\Program Files\eSpeak NG\espeak-ng.exe"
                        if os.path.exists(fallback_path):
                            espeak_exe = fallback_path

                    # 0x08000000 = CREATE_NO_WINDOW (Hides terminal popup)
                    flags = 0x08000000 
                    self.process = subprocess.Popen(
                        [espeak_exe, '-v', lang_code + '+f3', '--stdin'], # 👈 Add variant +f3 for smoother node
                        stdin=subprocess.PIPE,
                        creationflags=flags
                    )
                    self.process.stdin.write(text.encode('utf-8'))
                    self.process.stdin.close()
                    return
                except Exception as e:
                    print(f"🚨 [TTS ERROR] Failed to run espeak-ng fallback: {e}")
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
            if current_lang == "हिंदी": voice_arg = 'hi'
            elif current_lang == "മലയാളം": voice_arg = 'ml'
            else: voice_arg = 'en'
            
            self.process = subprocess.Popen(['espeak-ng', '-v', voice_arg, '-s', str(self.speech_rate), text])
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
        self.iterate_timer.timeout.connect(self.worker._iterate_windows_loop)
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