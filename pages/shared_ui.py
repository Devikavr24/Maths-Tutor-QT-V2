# pages/shared_ui.py

from PyQt5.QtWidgets import ( QWidget, QLabel, QHBoxLayout, QPushButton,
                              QVBoxLayout,QSizePolicy, QDialog, QSlider, QDialogButtonBox
                              ,QSpacerItem,QLineEdit,QMessageBox,QApplication,QShortcut )

from PyQt5.QtCore import Qt, QSize, QPoint, QTimer, QRegExp
from PyQt5.QtGui import QFont, QPalette, QColor, QKeySequence, QIcon, QRegExpValidator
from PyQt5.QtCore import QPropertyAnimation, QSequentialAnimationGroup
from question.loader import QuestionProcessor
from time import time
import random 
from tts.tts_worker import TextToSpeech
from PyQt5.QtMultimedia import QSound

from language.language import set_language,clear_remember_language,tr
from PyQt5.QtGui import QMovie

DIFFICULTY_LEVELS = ["Simple", "Easy", "Medium", "Hard", "Challenging"]


def create_entry_ui(main_window) -> QWidget:
    entry_widget = QWidget()
    entry_widget.setProperty("theme", main_window.current_theme) 
    layout = QVBoxLayout()
    layout.setAlignment(Qt.AlignCenter)

    label = QLabel("Click below to start the quiz")
    label.setFont(QFont("Arial", 24))
    label.setAlignment(Qt.AlignCenter)
    # ✅ ACCESSIBILITY: Screen reader announces instruction
    label.setAccessibleName("Click below to start the quiz")

    def start_quiz():
        print("Start button clicked")  # ✅ DEBUG POINT
        from pages.ques_functions import start_uploaded_quiz
        start_uploaded_quiz(main_window)
    
    button = create_menu_button("Start", start_quiz)
    # BUG FIX: Removed duplicate button.clicked.connect(start_quiz) — already connected in create_menu_button
    # ✅ ACCESSIBILITY: Clear accessible name for start button
    button.setAccessibleName("Start Quiz")
    button.setAccessibleDescription("Begin the uploaded quiz")

    layout.addWidget(label)
    layout.addSpacing(20)
    layout.addWidget(button, alignment=Qt.AlignCenter)

    entry_widget.setLayout(layout)
    apply_theme(entry_widget, main_window.current_theme)
    return entry_widget

# settings_manager.py
class SettingsManager:
    def __init__(self):
        self.difficulty_index = 1  # default Medium
        self.language = "English"

    def set_difficulty(self, index):
        self.difficulty_index = index

    def get_difficulty(self):
        return self.difficulty_index

    def set_language(self, lang):
        self.language = lang

    def get_language(self):
        return self.language


# Singleton instance to be imported anywhere
settings = SettingsManager()


def create_colored_widget(color: str = "#ffffff") -> QWidget:
    widget = QWidget()
    palette = widget.palette()
    palette.setColor(QPalette.Window, QColor(color))
    widget.setAutoFillBackground(True)
    widget.setPalette(palette)
    return widget

def create_label(text: str, font_size=16, bold=True) -> QLabel:
    label = QLabel(text)
    label.setWordWrap(True)  # allow wrapping of long text
    label.setAlignment(Qt.AlignCenter)  # center text
    font = QFont("Arial", font_size)
    font.setBold(bold)
    label.setFont(font)
    label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)  # allow resizing
    return label
   

def create_colored_page(title: str, color: str = "#d0f0c0") -> QWidget:
    page = create_colored_widget(color)
    layout = QVBoxLayout()
    layout.setAlignment(Qt.AlignCenter)

    title_label = create_label(title, font_size=20)
    answer_input = create_answer_input()

    layout.addWidget(title_label)
    layout.addSpacing(20)
    layout.addWidget(answer_input)

    page.setLayout(layout)
    return page


def create_menu_button(text, callback):
    button = QPushButton(text)
    button.setMinimumSize(200, 40)
    button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    button.setProperty("class", "menu-button")
    btn_clean = text.replace("⚡", "").replace("🎮", "").replace("🎓", "").strip()
    button.setAccessibleName(btn_clean)
    button.clicked.connect(callback)
    return button

def create_vertical_layout(widgets: list) -> QVBoxLayout:
    layout = QVBoxLayout()
    layout.setAlignment(Qt.AlignTop)  # Align to top so everything is visible
    for widget in widgets:
        widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(widget)
    return layout
   
def create_footer_buttons(names, callbacks=None, size=(90, 30)) -> QWidget:
    footer = QWidget()
    layout = QHBoxLayout()
    layout.setSpacing(10)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.addStretch()

    for name in names:
        btn = QPushButton(name)
        btn.setObjectName(name.lower().replace(" ", "_"))
        btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        btn.adjustSize() 
        btn.setFont(QFont("Arial", 14))  # or bigger
        btn.setProperty("class", "footer-button")
        # ✅ ACCESSIBILITY: Screen reader announces button name
        btn.setAccessibleName(name)
        if callbacks and name in callbacks:
            btn.clicked.connect(callbacks[name])
        layout.addWidget(btn)

    footer.setLayout(layout)
    return footer

def create_main_footer_buttons(self):
        buttons = ["Back to Menu", "Upload", "Settings"]
        translated = {tr(b): b for b in buttons}  

        footer = create_footer_buttons(
            list(translated.keys()),
            callbacks={
                tr("Back to Menu"): self.back_to_main_menu,
                tr("Upload"): self.handle_upload,
                tr("Settings"): self.handle_settings
            }
        )

        audio_btn = self.create_audio_button()
        footer.layout().insertWidget(0, audio_btn, alignment=Qt.AlignLeft)
        return footer

def create_answer_input(width=300, height=40, font_size=14) -> QLineEdit:
    input_box = QLineEdit()
    input_box.setMinimumSize(width, height)
    input_box.setAlignment(Qt.AlignCenter)
    input_box.setPlaceholderText(tr("Enter your answer"))
    input_box.setFont(QFont("Arial", font_size))
    input_box.setProperty("class", "answer-input")
    # Only allow digits, optional leading minus, and optional decimal point
    validator = QRegExpValidator(QRegExp(r"-?\d*\.?\d*"))
    input_box.setValidator(validator)
    return input_box

def wrap_center(widget):
    container = QWidget()
    layout = QHBoxLayout()
    layout.addStretch()             # Push from the left
    layout.addWidget(widget)        # The centered widget
    layout.addStretch()             # Push from the right
    container.setLayout(layout)
    return container

def setup_exit_handling(window, require_confirmation=False):
    """
    Configures exit behavior.
    - Ctrl+Q: Quits the Application (asks for confirmation if enabled).
    - Window Close (X): Closes the window (asks for confirmation if enabled).
    """

    # 1. Define the Exit Logic
    def check_and_close(event=None):
        if require_confirmation:
            # ✅ EXPLICIT DYNAMIC TRANSLATION (Bypassing tr() to guarantee it works)
            current_lang = getattr(window, 'language', 'English')
            
            title_text = tr("Exit Application")
            msg_text = tr("Are you sure you want to exit?")
            yes_text = tr("Yes")
            no_text = tr("No")

            msg_box = QMessageBox(window)
            msg_box.setWindowTitle(title_text)
            msg_box.setText(msg_text)
            
            yes_btn = msg_box.addButton(yes_text, QMessageBox.YesRole)
            no_btn = msg_box.addButton(no_text, QMessageBox.NoRole)
            msg_box.setDefaultButton(no_btn)
            
            msg_box.exec_()
            
            if msg_box.clickedButton() == yes_btn:
                if event: event.accept()
                else: QApplication.quit()
            else:
                if event: event.ignore()
        else:
            # No confirmation needed
            if event: event.accept()
            else: QApplication.quit()

    # 2. Handle Ctrl+Q (Quit App)
    if hasattr(window, "quit_shortcut"): 
        # Remove old shortcut if it exists to avoid duplicates
        window.quit_shortcut.setParent(None)
        
    window.quit_shortcut = QShortcut(QKeySequence("Ctrl+Q"), window)
    window.quit_shortcut.setContext(Qt.ApplicationShortcut)
    window.quit_shortcut.setWhatsThis("Press Ctrl+Q to quit the application")
    window.quit_shortcut.activated.connect(lambda: check_and_close(event=None))

    # 3. Handle X Button (Close Window)
    window.closeEvent = check_and_close


class QuestionWidget(QWidget):
    def __init__(self, processor, window=None, next_question_callback=None, tts=None):
        super().__init__()
        # ✅ ACCESSIBILITY: Prevent NVDA from announcing this container as "grouping"
        self.setAccessibleName("")
        self.setAccessibleDescription("")
        self.processor = processor
        self.answer = None
        self.start_time = time()
        self.next_question_callback = next_question_callback
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)
        self.main_window = window
        self.setProperty("theme", window.current_theme)
        if tts:
            self.tts = tts
        else:
            self.tts = TextToSpeech()
        self._question_count = 0  # Track question number for TTS timing
        self.is_bell_mode = (processor.questionType.lower() == "bellring")
        self.bell_press_count = 0
        self._active = True  # Guard flag for stale QTimer callbacks
        self.init_ui()
       
    def init_ui(self):
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setProperty("class", "question-label")
        self.label.setWordWrap(True)
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        if self.is_bell_mode:
            # ── Bell Ring Mode: button instead of text input ──
            self.input_box = None  # Guard for code that references input_box

            self.bell_button = QPushButton("")
            self.bell_button.setIcon(QIcon("images/bell.png"))
            self.bell_button.setIconSize(QSize(128, 128))
            self.bell_button.setMinimumSize(150, 150)
            self.bell_button.setFlat(True)
            self.bell_button.setStyleSheet("border: none; background: transparent;")
            self.bell_button.clicked.connect(self._on_bell_pressed)

            # Pause-detection timer (single-shot, 1.5s)
            self.bell_pause_timer = QTimer(self)
            self.bell_pause_timer.setSingleShot(True)
            self.bell_pause_timer.setInterval(1500)
            self.bell_pause_timer.timeout.connect(self._evaluate_bell_answer)
        else:
            # ── Standard Mode: text input ──
            self.bell_button = None
            self.bell_pause_timer = None

            self.input_box = create_answer_input()
            # FIX: Remove visual placeholder to stop "double reading" (Label + Placeholder)
            self.input_box.setPlaceholderText("")
            self.input_box.returnPressed.connect(self.check_answer)

        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setFont(QFont("Arial", 46))

        # Assemble layout with references for dynamic scaling
        self.top_spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.layout.addSpacerItem(self.top_spacer)
        
        self.layout.addWidget(self.label)
        
        self.mid_spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.layout.addSpacerItem(self.mid_spacer)
        
        self.input_spacing_item = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.layout.addSpacerItem(self.input_spacing_item)

        if self.is_bell_mode:
            self.layout.addWidget(self.bell_button, alignment=Qt.AlignCenter)
        else:
            self.layout.addWidget(self.input_box, alignment=Qt.AlignCenter)

        self.result_spacing_item = QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.layout.addSpacerItem(self.result_spacing_item)
        
        self.layout.addWidget(self.result_label)
        self.layout.addStretch()

        self.gif_feedback_label = QLabel()
        self.gif_feedback_label.setVisible(False)
        self.gif_feedback_label.setAlignment(Qt.AlignCenter)
        self.gif_feedback_label.setScaledContents(True)
        self.gif_feedback_label.setMinimumSize(300, 300)
        self.gif_feedback_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # ✅ ACCESSIBILITY: Mark decorative feedback animation as hidden from screen readers
        self.gif_feedback_label.setAccessibleName("")
        self.gif_feedback_label.setAccessibleDescription("")

        self.layout.addWidget(self.gif_feedback_label, alignment=Qt.AlignCenter)

        self.load_new_question()

    def update_scaling(self, scale):
        if hasattr(self, 'gif_feedback_label') and self.gif_feedback_label:
            target_size = int(220 * scale)
            target_size = min(max(150, target_size), 450)
            self.gif_feedback_label.setFixedSize(target_size, target_size)
            
        if hasattr(self, 'bell_button') and self.bell_button:
            target_size = int(140 * scale)
            self.bell_button.setMinimumSize(target_size, target_size)
            self.bell_button.setIconSize(QSize(target_size - 18, target_size - 18))
        elif hasattr(self, 'input_box') and self.input_box:
            self.input_box.setFixedHeight(int(55 * scale))
            self.input_box.setMinimumWidth(int(380 * scale))
            
        # Dynamically scale layout spacer heights 
        if hasattr(self, 'top_spacer'):
            self.top_spacer.changeSize(20, int(40 * scale), QSizePolicy.Minimum, QSizePolicy.Expanding)
        if hasattr(self, 'mid_spacer'):
            self.mid_spacer.changeSize(20, int(40 * scale), QSizePolicy.Minimum, QSizePolicy.Expanding)
        if hasattr(self, 'input_spacing_item'):
            self.input_spacing_item.changeSize(20, int(25 * scale), QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.layout.invalidate() 

    def show_feedback_gif(self, sound_filename):
        if sound_filename == "question":
            gif_name = f"question-{random.choice([1, 2])}.gif"
        else:  
            gif_name = sound_filename.replace(".mp3", ".gif")
        gif_path = f"images/{gif_name}"

        movie = QMovie(gif_path)
        movie.setScaledSize(QSize(200, 200))
        self.gif_feedback_label.setFixedSize(200, 200)
        self.gif_feedback_label.setAlignment(Qt.AlignCenter)
        self.gif_feedback_label.setMovie(movie)
        self.gif_feedback_label.setVisible(True)
        movie.start()
            
    def hide_feedback_gif(self):
        self.gif_feedback_label.setVisible(False)
        self.gif_feedback_label.clear()

    def end_session(self):
        self.main_window.bg_player.stop()   
        if self.main_window:
            self.main_window.back_to_main_menu()

    def set_input_focus(self):
        # FIX: Only set focus if we actually LOST it.
        # Forcing focus on an already focused element causes screen readers to re-announce.
        if self.is_bell_mode:
            if self.bell_button and not self.bell_button.hasFocus():
                self.bell_button.setFocus()
        elif self.input_box:
            if not self.input_box.hasFocus():
                self.input_box.setFocus()

    def load_new_question(self):
        if hasattr(self, "gif_feedback_label"):
            self.hide_feedback_gif()

        question_text, self.answer = self.processor.get_questions()
        self._active = True  # Re-enable for new question
        self.start_time = time()

        # --- TTS START ---
        app_tts_active = False
        if self.main_window and not self.main_window.is_muted:
            app_tts_active = True
        
        if self.processor.questionType.lower() == "bellring":
            app_tts_active = False

        if app_tts_active:
            if hasattr(self, 'tts'):
                current_lang = getattr(self.main_window, 'language', 'English')
                instruction = tr("Type your answer")
                tts_text = f"{question_text}. {instruction}"
                
                if self._question_count == 0:
                    QTimer.singleShot(10, lambda: self.tts.speak(tts_text))
                else:
                    self.tts.speak(tts_text)

        # Dynamically Adjust Font Size for long questions
        text_len = len(question_text)
        if text_len > 140:
            self.label.setStyleSheet("font-size: 14pt;")
        elif text_len > 100:
            self.label.setStyleSheet("font-size: 16pt;")
        elif text_len > 60:
            self.label.setStyleSheet("font-size: 19pt;")
        else:
            self.label.setStyleSheet("") # Revert to stylesheet default
            
        self.label.setText(question_text)

        if self.input_box:
            self.input_box.clear()
        self.result_label.setText("")
        self.show_feedback_gif("question")

        # Reset bell press counter for new question
        if self.is_bell_mode:
            self.bell_press_count = 0
            if self.bell_pause_timer and self.bell_pause_timer.isActive():
                self.bell_pause_timer.stop()
        
                    
        # --- Bell Ring Question Audio ---
        if self.processor.questionType.lower() == "bellring":
             # Delay slightly to allow UI to settle if it's the first question, 
             # matching the TTS delay logic above
             delay = 500 if self._question_count == 0 else 100
             print(f"[BellRing] Scheduling sequence for: {question_text}")
             QTimer.singleShot(delay, lambda: self.play_bell_question_sequence(question_text))

        # Defer focus to the appropriate input widget
        if self.is_bell_mode:
            QTimer.singleShot(100, lambda: self.bell_button.setFocus(Qt.OtherFocusReason))
        elif self.input_box:
            QTimer.singleShot(100, lambda: self.input_box.setFocus(Qt.OtherFocusReason))

        self._question_count += 1
        # --- END ---

   
    def play_bell_sounds(self, count):
        if not hasattr(self, "bell_timer"):
            self.bell_timer = QTimer(self)
            self.bell_timer.timeout.connect(self.do_ring)
        self.current_ring = 0
        self.total_rings = count
        self.bell_timer.start(700)

    def stop_all_activity(self):
        self._active = False  # Prevent stale QTimer.singleShot callbacks

        if hasattr(self, "bell_timer") and self.bell_timer.isActive():
            self.bell_timer.stop()
        
        # Stop Bell Sequence Timer (Phase 1 & 3)
        if hasattr(self, "bell_seq_timer") and self.bell_seq_timer.isActive():
            self.bell_seq_timer.stop()
            
        # Stop Sequence Wait Timer (Phase 2 -> 3 transition)
        if hasattr(self, "seq_timer") and self.seq_timer.isActive():
            self.seq_timer.stop()

        # Stop Bell Pause Timer (user answer pause detection)
        if hasattr(self, "bell_pause_timer") and self.bell_pause_timer and self.bell_pause_timer.isActive():
            self.bell_pause_timer.stop()

    def do_ring(self):
        if self.current_ring < self.total_rings:
            QSound.play("sounds/click-button.wav")
            self.current_ring += 1
        else:
            self.bell_timer.stop()


    def check_answer(self):
            from language.language import tr
            # ✅ Stop any ongoing bell sequences or audio immediately when user answers
            self.stop_all_activity()
            self._active = True  # Re-enable: user is answering, not navigating away

            if not self.input_box:
                return  # Bell mode uses _evaluate_bell_answer instead

            user_input = self.input_box.text().strip()
            elapsed = time() - self.start_time

            result = self.processor.submit_answer(user_input, self.answer, elapsed)


            # ✅ Check current language for dynamic translations
            current_lang = getattr(self.main_window, 'language', 'English')

            if not result["valid"]:
                invalid_msg = tr("Please enter a valid number.")
                self.result_label.setText(invalid_msg)
                self.result_label.setAccessibleName(invalid_msg)
                return

            correct = result["correct"]
            self._last_result = {
                'correct': correct,
                'elapsed': elapsed,
                'skill': self.processor.questionType
            }

            app_audio_active = False
            if self.main_window and not self.main_window.is_muted:
                app_audio_active = True

            if correct:
                if hasattr(self, 'tts'): self.tts.stop()

                # ✅ TRANSLATED: "Correct!"
                correct_text = tr("Correct!")
                
                sound_index = random.randint(1, 3)
                
                # Dynamically scale thresholds for long questions
                time_offset = len(self.label.text()) // 30 # 1s per 30 chars
                
                # Map thresholds to lookup Keys, Emojis, and SFX prefixes
                feedback_tiers = [
                    (5 + time_offset, "Excellent", "🌟", "excellent"),
                    (10 + time_offset, "Very Good", "👏", "very-good"),
                    (15 + time_offset, "Good", "👍", "good"),
                    (20 + time_offset, "Not Bad", "👌", "not-bad"),
                    (float('inf'), "Okay", "🙂", "okay")
                ]
                
                feedback_key = "Okay"; emoji = "🙂"; sound_file = f"okay-{sound_index}.mp3" # Fallback
                for limit, key, emj, prefix in feedback_tiers:
                    if elapsed < limit:
                        feedback_key = key
                        emoji = emj
                        sound_file = f"{prefix}-{sound_index}.mp3"
                        break
                
                feedback_text = f"{emoji} " + tr(feedback_key)
                self.result_label.setText(f'<span style="font-size:16pt;">{feedback_text}</span>')
                
                # ✅ ACCESSIBILITY: Update accessible name with clean feedback
                clean_feedback = tr(feedback_key)
                self.result_label.setAccessibleName(f"{correct_text} {clean_feedback}")
                
                if app_audio_active and self.main_window:
                    self.main_window.play_sound(sound_file)
                    self.show_feedback_gif(sound_file)
                    
                    # ✅ TTS FEEDBACK: Announce translated feedback after a short delay
                    if hasattr(self, 'tts'):
                        QTimer.singleShot(10, lambda t=clean_feedback: self.tts.speak(t))
                        
                self.processor.retry_count = 0
                QTimer.singleShot(2000, self.call_next_question)
                return # Skip remaining logic


            else:
                self.processor.retry_count += 1
                from language.language import tr

                if hasattr(self.main_window, 'game_active') and self.main_window.game_active and self.processor.retry_count >= 2:
                    self.result_label.setText(f'<span style="font-size:16pt;">{tr("Let\'s try another one!")}</span>')
                    QTimer.singleShot(2000, self.call_next_question)
                    return

                # ✅ TRANSLATED: "Try Again" visual and speech
                try_again_visual = tr("Try Again.")
                try_again_tts = tr("Try Again.")
                incorrect_tts = tr("Incorrect.")
                
                self.result_label.setText(f'<span style="font-size:16pt;">{try_again_visual}</span>')
                self.result_label.setAccessibleName(f"{incorrect_tts} {try_again_tts}")


                if app_audio_active:
                    sound_index = random.randint(1, 2)
                    if self.processor.retry_count == 1: sound_file = f"wrong-anwser-{sound_index}.mp3"
                    else: sound_file = f"wrong-anwser-repeted-{sound_index}.mp3"
                    
                    self.main_window.play_sound(sound_file)
                    self.show_feedback_gif(sound_file)
                    
                    if hasattr(self, 'tts'):
                        QTimer.singleShot(300, lambda t=try_again_tts: self.tts.speak(t))

                # Focus remains on Input Box.
                if not self.input_box.hasFocus():
                    self.input_box.setFocus()
       

    def call_next_question(self):
        if not self._active:
            return
        if hasattr(self, "next_question_callback") and self.next_question_callback:
            self.next_question_callback()
        else:
            self.load_new_question()

    # --- Bell Ring Sequence Logic ---
    def play_bell_question_sequence(self, question_text):
        if not self._active:
            return
        # Stop any existing sequence first
        self.stop_all_activity()
        self._active = True  # Re-enable after stop_all_activity sets it False

        print(f"[BellRing] processing sequence for: '{question_text}'")

        import re
        # Parse "3 + 2" or "3 + 2 =" or "3 + 2 = ?"
        match = re.search(r'(\d+)\s*([+\-*/×xX])\s*(\d+)', question_text)
        
        if not match:
            print(f"[BellRing] Could not parse question for audio: '{question_text}' - Type: {self.processor.questionType}")
            # Fallback to just reading it if parsing fails
            if hasattr(self, 'tts') and self.tts: 
                self.tts.speak(question_text)
            return

        num1 = int(match.group(1))
        op_char = match.group(2)
        num2 = int(match.group(3))

        op_map = {
            '+': "Addition",
            '-': "Subtraction",
            '*': "Multiplication",
            '×': "Multiplication",
            'x': "Multiplication",
            'X': "Multiplication",
            '/': "Division",
            '÷': "Division"
        }
        self.seq_op_text = op_map.get(op_char, "Operation")
        self.seq_num2 = num2

        print(f"[BellRing] Parsed: {num1} {op_char} {num2} -> {self.seq_op_text}")

        # Start Sequence: Phase 1 (First Operand Bells)
        self.play_bells_with_callback(num1, self._seq_phase_2_speak_op)

    def _seq_phase_2_speak_op(self):
        if not self._active:
            return
        # Phase 2: Speak Operator
        if hasattr(self, 'tts') and self.tts:
            self.tts.speak(self.seq_op_text)
        # Wait 1.5s for speech to finish, then Phase 3
        self.seq_timer = QTimer(self)
        self.seq_timer.setSingleShot(True)
        self.seq_timer.timeout.connect(self._seq_phase_3_second_operand)
        self.seq_timer.start(1500)

    def _seq_phase_3_second_operand(self):
        if not self._active:
            return
        # Phase 3: Second Operand Bells
        self.play_bells_with_callback(self.seq_num2, self._seq_phase_4_done)

    def _seq_phase_4_done(self):
        if not self._active:
            return
        # Sequence complete — in bell mode, prompt user to ring their answer
        if self.is_bell_mode:
            if hasattr(self, 'tts') and self.tts and self.main_window and not self.main_window.is_muted:
                QTimer.singleShot(300, lambda: self.tts.speak("Now ring your answer"))
            # Focus the bell button after a short delay
            QTimer.singleShot(500, lambda: self.bell_button.setFocus(Qt.OtherFocusReason))

    def play_bells_with_callback(self, count, callback):
        """Plays bell 'count' times, then calls 'callback'."""
        
        # Stop any existing bell sequence timer to prevent overlaps
        if hasattr(self, "bell_seq_timer") and self.bell_seq_timer.isActive():
            self.bell_seq_timer.stop()

        if count <= 0:
            if callback: callback()
            return

        self.bell_seq_counter = 0
        self.bell_seq_total = count
        self.bell_seq_callback = callback
        
        # Use a timer for the intervals
        self.bell_seq_timer = QTimer(self)
        self.bell_seq_timer.timeout.connect(self._on_bell_seq_tick)
        self.bell_seq_timer.start(600) # 600ms gap between bells
        
        # Play first one immediately
        self._on_bell_seq_tick() 

    def _on_bell_seq_tick(self):
        if self.bell_seq_counter < self.bell_seq_total:
            if self.main_window:
                self.main_window.play_sound("BellRing.mp3")
            self.bell_seq_counter += 1
        else:
            self.bell_seq_timer.stop()
            if self.bell_seq_callback:
                self.bell_seq_callback()

    # ── Bell Ring Mode: button press handling ──
    def _on_bell_pressed(self):
        """Called each time user clicks the Ring Bell button."""
        self.bell_press_count += 1
        print(f"[BellRing] Press #{self.bell_press_count}")
        # Vibration animation
        self._shake_bell()
        # Play bell sound on each press
        if self.main_window and not self.main_window.is_muted:
            self.main_window.play_sound("BellRing.mp3")
        # Restart pause timer on each press
        if self.bell_pause_timer:
            self.bell_pause_timer.stop()
            self.bell_pause_timer.start(1500)

    def _shake_bell(self):
        """Subtle vibration animation on the bell button."""
        if not self.bell_button:
            return
        origin = self.bell_button.pos()
        anim_group = QSequentialAnimationGroup(self)

        offsets = [4, -8, 6, -4, 2, 0]  # pixel offsets for shake
        for dx in offsets:
            anim = QPropertyAnimation(self.bell_button, b"pos")
            anim.setDuration(35)
            anim.setEndValue(QPoint(origin.x() + dx, origin.y()))
            anim_group.addAnimation(anim)

        anim_group.start()
        # Keep a reference so it doesn't get garbage collected mid-animation
        self._shake_anim = anim_group

    def _evaluate_bell_answer(self):
        """Called when the pause timer fires after the user stops pressing."""
        count = self.bell_press_count
        self.bell_press_count = 0  # Reset for next sequence

        try:
            correct_answer = int(self.answer)
        except (ValueError, TypeError):
            correct_answer = -1  # Safety fallback

        elapsed = time() - self.start_time
        is_correct = (count == correct_answer)
        self._last_result = {
            'correct': is_correct,
            'elapsed': elapsed,
            'skill': self.processor.questionType
        }

        app_audio_active = self.main_window and not self.main_window.is_muted

        print(f"[BellRing] Evaluating: pressed {count}, answer {correct_answer}, correct={is_correct}")

        if is_correct:
            if hasattr(self, 'tts'):
                self.tts.stop()

            # Feedback
            sound_index = random.randint(1, 3)
            if elapsed < 5: feedback_text = "🌟 Excellent"
            elif elapsed < 10: feedback_text = "👏 Very Good"
            elif elapsed < 15: feedback_text = "👍 Good"
            elif elapsed < 20: feedback_text = "👌 Not Bad"
            else: feedback_text = "🙂 Okay"

            self.result_label.setText(f'<span style="font-size:16pt;">{feedback_text}</span>')
            clean_feedback = feedback_text.replace("🌟", "").replace("👏", "").replace("👍", "").replace("👌", "").replace("🙂", "").strip()
            self.result_label.setAccessibleName(f"Correct! {clean_feedback}")

            if app_audio_active and self.main_window:
                if elapsed < 5: sound_file = f"excellent-{sound_index}.mp3"
                elif elapsed < 10: sound_file = f"very-good-{sound_index}.mp3"
                elif elapsed < 15: sound_file = f"good-{sound_index}.mp3"
                elif elapsed < 20: sound_file = f"not-bad-{sound_index}.mp3"
                else: sound_file = f"okay-{sound_index}.mp3"

                self.main_window.play_sound(sound_file)
                self.show_feedback_gif(sound_file)

                if hasattr(self, 'tts'):
                    QTimer.singleShot(300, lambda t=clean_feedback: self.tts.speak(t))

            self.processor.retry_count = 0
            QTimer.singleShot(2000, self.call_next_question)

        else:
            self.processor.retry_count += 1
            from language.language import tr

            if hasattr(self.main_window, 'game_active') and self.main_window.game_active and self.processor.retry_count >= 2:
                self.result_label.setText(f'<span style="font-size:16pt;">{tr("Let\'s try another one!")}</span>')
                QTimer.singleShot(2000, self.call_next_question)
                return

            self.result_label.setText('<span style="font-size:16pt;">Try Again.</span>')
            self.result_label.setAccessibleName("Incorrect. Try Again.")


            if app_audio_active and self.main_window:
                sound_index = random.randint(1, 2)
                if self.processor.retry_count == 1:
                    sound_file = f"wrong-anwser-{sound_index}.mp3"
                else:
                    sound_file = f"wrong-anwser-repeted-{sound_index}.mp3"

                self.main_window.play_sound(sound_file)
                self.show_feedback_gif(sound_file)

                if hasattr(self, 'tts'):
                    QTimer.singleShot(300, lambda: self.tts.speak("Try Again"))

            # Keep focus on bell button for retry
            if self.bell_button and not self.bell_button.hasFocus():
                self.bell_button.setFocus()



def create_dynamic_question_ui(section_name, difficulty_index, back_callback,main_window=None, back_to_operations_callback=None, tts=None):
    container = QWidget()
    # ✅ ACCESSIBILITY: Prevent NVDA from announcing this container as "grouping"
    container.setAccessibleName("")
    container.setAccessibleDescription("")
    layout = QVBoxLayout()
    layout.setAlignment(Qt.AlignTop)
    container.setLayout(layout)

    # ✅ Temporary: Force difficulty to 1 for Bell Ring mode
    if section_name.lower() == "bellring":
        print(f"[BellRing] Overriding difficulty {difficulty_index} -> 1")
        difficulty_index = 1

    processor = QuestionProcessor(section_name, difficulty_index)
    processor.process_file()
    
    question_widget = QuestionWidget(processor,main_window, tts=tts)

    layout.addWidget(question_widget)
    apply_theme(container, main_window.current_theme)
    return container


def apply_theme(widget, theme):
    if not widget:
        return

    widget.setProperty("theme", theme)
    widget.style().unpolish(widget)
    widget.style().polish(widget)
    widget.update()

    for child in widget.findChildren(QWidget):  # covers all widgets
        child.setProperty("theme", theme)
        child.style().unpolish(child)
        child.style().polish(child)
        child.update()

class SettingsDialog(QDialog):
    def __init__(self, parent=None, initial_difficulty=1, main_window=None):
        super().__init__(parent)
        
        self.main_window = main_window
        self.updated_language = main_window.language if main_window else "English"
        
        title_text = tr("Settings")
        
        self.setWindowTitle(title_text)
        self.setFixedSize(400, 220)

        self.difficulty_slider = QSlider(Qt.Horizontal)
        self.difficulty_slider.setMinimum(0)
        self.difficulty_slider.setMaximum(len(DIFFICULTY_LEVELS) - 1)
        self.difficulty_slider.setSingleStep(1)
        self.difficulty_slider.setPageStep(1)
        self.difficulty_slider.setTickInterval(1)
        self.difficulty_slider.setTickPosition(QSlider.TicksBelow)
        self.difficulty_slider.setTracking(True)
        self.difficulty_slider.setAccessibleName(tr("Difficulty")) 
        
        self.difficulty_slider.setValue(initial_difficulty)
        
        # ✅ FIX: Initial Difficulty Label Localization
        localized_initial_level = self.get_localized_difficulty(initial_difficulty)
        self.difficulty_label = create_label(localized_initial_level, font_size=12)
        
        self.difficulty_label.setProperty("class", "difficulty-label")
        self.difficulty_label.setProperty("theme", parent.current_theme)
        self.difficulty_label.setAccessibleName(" ")

        self.difficulty_slider.valueChanged.connect(self.update_difficulty_label)
        
        QTimer.singleShot(250, lambda: self.difficulty_slider.setFocus())
        self.setProperty("theme", parent.current_theme)
        
        # ✅ EXPLICIT DYNAMIC TRANSLATION
        reset_text = tr("Reset Language")
        self.language_reset_btn = QPushButton(reset_text)
        self.language_reset_btn.setFixedHeight(30)
        self.language_reset_btn.clicked.connect(self.handle_reset_language)
        self.language_reset_btn.setAccessibleName(reset_text)
        self.language_reset_btn.setAccessibleDescription(tr("Clear saved language preference and choose a new language"))

        # ✅ EXPLICIT DYNAMIC TRANSLATION FOR OK/CANCEL
        ok_text = tr("OK")
        cancel_text = tr("Cancel")
        
        button_box = QDialogButtonBox()
        ok_btn = button_box.addButton(ok_text, QDialogButtonBox.AcceptRole)
        cancel_btn = button_box.addButton(cancel_text, QDialogButtonBox.RejectRole)
        
        button_box.accepted.connect(self.accept_settings)
        button_box.rejected.connect(self.reject)
        
        ok_btn.setAccessibleName(tr("OK — Apply settings"))
        cancel_btn.setAccessibleName(tr("Cancel — Discard changes"))

        self.setMinimumSize(400, 280)

        layout = QVBoxLayout()
        layout.setSpacing(12) 
        layout.setContentsMargins(20, 20, 20, 20)

        # ✅ EXPLICIT DYNAMIC TRANSLATION
        diff_label_text = tr("Select Difficulty:")
        difficulty_label = QLabel(diff_label_text)
        difficulty_label.setProperty("class", "difficulty-label")
        difficulty_label.setProperty("theme", parent.current_theme)
        difficulty_label.setAccessibleName(tr("Select Difficulty. Use left or right arrow keys to select difficulty level.")) 
        difficulty_label.setBuddy(self.difficulty_slider)
        
        layout.addWidget(difficulty_label)
        layout.addWidget(self.difficulty_slider)
        layout.addWidget(self.difficulty_label)
        layout.addWidget(self.language_reset_btn)

        # ✅ EXPLICIT DYNAMIC TRANSLATION
        help_text = tr("Help")
        about_text = tr("About")
        
        extra_buttons_layout = QHBoxLayout()
        self.help_button = QPushButton(help_text)
        self.about_button = QPushButton(about_text)
        
        for btn in [self.help_button, self.about_button]:
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            btn.setFixedHeight(30)
            
        self.help_button.setAccessibleName(help_text)
        self.about_button.setAccessibleName(about_text)
        
        extra_buttons_layout.addWidget(self.help_button)
        extra_buttons_layout.addWidget(self.about_button)
        layout.addLayout(extra_buttons_layout)

        layout.addStretch()
        layout.addWidget(button_box)

        self.setLayout(layout)

        # Accessibility Tab Order
        QWidget.setTabOrder(self.difficulty_slider, self.language_reset_btn)
        QWidget.setTabOrder(self.language_reset_btn, self.help_button)
        QWidget.setTabOrder(self.help_button, self.about_button)
        if ok_btn and cancel_btn:
            QWidget.setTabOrder(self.about_button, ok_btn)
            QWidget.setTabOrder(ok_btn, cancel_btn)

    # ✅ FIX: Helper function for Difficulty Translation
    def get_localized_difficulty(self, index):
        eng_level = DIFFICULTY_LEVELS[index]
        if self.updated_language == "हिंदी":
            hindi_map = {
                "Simple": "सरल",
                "Easy": "आसान",
                "Medium": "मध्यम",
                "Hard": "कठिन",
                "Challenging": "चुनौतीपूर्ण"
            }
            return hindi_map.get(eng_level, eng_level)
        return eng_level

    def update_difficulty_label(self, index):
        # ✅ FIX: Dynamically update the slider label and text-to-speech
        localized_level = self.get_localized_difficulty(index)
        self.difficulty_label.setText(localized_level)
        self.difficulty_label.setAccessibleName(" ")

        if self.main_window and hasattr(self.main_window, 'tts') and not self.main_window.is_muted:
             self.main_window.tts.stop()
             QTimer.singleShot(200, lambda: self.main_window.tts.speak(localized_level))

    def handle_reset_language(self):
        from main import RootWindow 
        from language.language import clear_remember_language, set_language

        clear_remember_language()
        
        dialog = RootWindow(minimal=True)
        if dialog.exec_() == QDialog.Accepted:
            new_lang = dialog.language_combo.currentText()
            
            set_language(new_lang)
            self.updated_language = new_lang

            QMessageBox.information(self, tr("Language Changed"),
                                    tr("Language changed to {new_lang}. The app will now reload.").format(new_lang=new_lang))

            if self.main_window:
                self.main_window.refresh_ui(new_lang)

            self.close() 

    def accept_settings(self):
        selected_index = self.difficulty_slider.value()
        settings.set_difficulty(selected_index)
        settings.set_language(self.updated_language)
        self.accept()
    def get_difficulty_index(self):
        return self.difficulty_slider.value()

    def get_selected_language(self):
        return self.updated_language

class GameReportWidget(QWidget):
    def __init__(self, session, window, tts):
        super().__init__()
        self.session = session
        self.main_window = window
        self.tts = tts
        self.setAccessibleName("")
        self.setAccessibleDescription("")

        # Calculate advancement eligibility
        avg_skill = sum(session.skill_scores.values()) / len(session.skill_scores)
        self.can_advance = (
            avg_skill >= 65 and
            session.questions_answered >= 10 and
            session.difficulty_index < 4
        )

        self.report_text = session.generate_report()
        self.init_ui()
        self._speak_report()

    def init_ui(self):
        from language.language import tr
        levels = ["Simple", "Easy", "Medium", "Hard", "Challenging"]
        
        layout = QVBoxLayout()

        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 20, 30, 20)
        self.setLayout(layout)

        # Title
        title = QLabel(tr("Session Complete!"))
        title.setAlignment(Qt.AlignCenter)
        title.setProperty("class", "main-title")
        layout.addWidget(title)

        # Report text
        report_label = QLabel(self.report_text)
        report_label.setAlignment(Qt.AlignCenter)
        report_label.setProperty("class", "subtitle")
        report_label.setWordWrap(True)
        report_label.setAccessibleName(self.report_text)
        layout.addWidget(report_label)

        layout.addSpacing(10)

        # Cards
        ranked = sorted(self.session.skill_scores.items(), key=lambda x: x[1], reverse=True)
        strengths = [s for s, score in ranked if score >= 60][:2]
        weakness = [s for s, score in ranked if score < 45][:1]

        if strengths:
            strength_row = QHBoxLayout()
            strength_row.setAlignment(Qt.AlignCenter)
            for skill in strengths:
                card = self._make_card(skill, "superpower", "teal")
                strength_row.addWidget(card)
            layout.addLayout(strength_row)

        if weakness:
            weak_row = QHBoxLayout()
            weak_row.setAlignment(Qt.AlignCenter)
            card = self._make_card(weakness[0], "next adventure", "coral")
            weak_row.addWidget(card)
            layout.addLayout(weak_row)

        cur_level = levels[self.session.difficulty_index] if self.session.difficulty_index < len(levels) else ""
        info_label = QLabel(f"{self.session.questions_answered} {tr('questions answered')} · {tr('Level')}: {tr(cur_level)}")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setProperty("class", "subtitle")
        layout.addWidget(info_label)

        layout.addSpacing(10)

        # Action Buttons
        btn_row = QHBoxLayout()
        btn_row.setAlignment(Qt.AlignCenter)
        btn_row.setSpacing(20)

        current_name = tr(cur_level)

        if self.can_advance:
            next_name = tr(levels[self.session.difficulty_index + 1])
            self.primary_btn = QPushButton(tr("Next Level: {level}").format(level=next_name))
            self.primary_btn.setMinimumHeight(65)
            self.primary_btn.setProperty("class", "menu-button")
            self.primary_btn.setProperty("theme", self.main_window.current_theme)
            self.primary_btn.setAccessibleName(tr("Next Level: {level}").format(level=next_name))
            self.primary_btn.clicked.connect(self._go_next_level)
            btn_row.addWidget(self.primary_btn)

        self.replay_btn = QPushButton(tr("Play {level} Again").format(level=current_name))
        self.replay_btn.setMinimumHeight(65)
        self.replay_btn.setProperty("class", "menu-button")
        self.replay_btn.setProperty("theme", self.main_window.current_theme)
        self.replay_btn.setAccessibleName(tr("Play {level} Again").format(level=current_name))
        self.replay_btn.clicked.connect(self._replay_level)
        btn_row.addWidget(self.replay_btn)

        layout.addLayout(btn_row)

    def _make_card(self, title, subtitle, card_type):
        from language.language import tr
        card = QWidget()
        card.setProperty("theme", self.main_window.current_theme)
        card.setProperty("class", "central-widget")
        
        card_layout = QVBoxLayout(card)
        card_layout.setAlignment(Qt.AlignCenter)
        card_layout.setContentsMargins(20, 15, 20, 15)
        card.setMinimumSize(150, 80)
        
        if card_type == "teal":
            card.setStyleSheet("QWidget { border: 2px solid #1D9E75; border-radius: 10px; }")
        else:
            card.setStyleSheet("QWidget { border: 2px solid #D85A30; border-radius: 10px; }")
        
        title_label = QLabel(tr(title))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setProperty("class", "subtitle")
        
        sub_label = QLabel(tr(subtitle))
        sub_label.setAlignment(Qt.AlignCenter)
        sub_label.setProperty("class", "subtitle")
        
        card_layout.addWidget(title_label)
        card_layout.addWidget(sub_label)
        return card

    def _speak_report(self):
        from language.language import tr
        QTimer.singleShot(800, lambda: self.tts.speak(self.report_text))

        estimated_ms = len(self.report_text) * 65
        choice_text = tr("Ready for the next level?") if self.can_advance else tr("Play again?")

        QTimer.singleShot(800 + estimated_ms, lambda: self.tts.speak(choice_text))

        focus_delay = 800 + estimated_ms + len(choice_text) * 65
        primary = self.primary_btn if self.can_advance else self.replay_btn
        QTimer.singleShot(focus_delay, lambda: primary.setFocus())

    def _go_next_level(self):
        self.tts.stop()
        self.main_window.load_game_questions(self.session.difficulty_index + 1)

    def _replay_level(self):
        self.tts.stop()
        self.main_window.load_game_questions(self.session.difficulty_index)

