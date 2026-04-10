# pages/shared_ui.py

from PyQt5.QtWidgets import ( QWidget, QLabel, QHBoxLayout, QPushButton,
                              QVBoxLayout, QSizePolicy, QDialog, QSlider, QDialogButtonBox,
                              QSpacerItem, QLineEdit, QMessageBox, QApplication, QShortcut,
                              QFrame )

from PyQt5.QtCore import Qt, QSize, QPoint, QTimer, QRegExp
from PyQt5.QtGui import QFont, QPalette, QColor, QKeySequence, QIcon, QRegExpValidator
from PyQt5.QtCore import QPropertyAnimation, QSequentialAnimationGroup
from question.loader import QuestionProcessor
from time import time
import random
from tts.tts_worker import TextToSpeech
from PyQt5.QtMultimedia import QSound

from language.language import set_language, clear_remember_language, tr
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
    label.setAccessibleName("Click below to start the quiz")

    def start_quiz():
        print("Start button clicked")
        from pages.ques_functions import start_uploaded_quiz
        start_uploaded_quiz(main_window)

    button = create_menu_button("Start", start_quiz)
    button.setAccessibleName("Start Quiz")
    button.setAccessibleDescription("Begin the uploaded quiz")

    layout.addWidget(label)
    layout.addSpacing(20)
    layout.addWidget(button, alignment=Qt.AlignCenter)

    entry_widget.setLayout(layout)
    apply_theme(entry_widget, main_window.current_theme)
    return entry_widget


class SettingsManager:
    def __init__(self):
        self.difficulty_index = 1
        self.language = "English"

    def set_difficulty(self, index):
        self.difficulty_index = index

    def get_difficulty(self):
        return self.difficulty_index

    def set_language(self, lang):
        self.language = lang

    def get_language(self):
        return self.language


settings = SettingsManager()


def create_colored_widget(color: str = "#ffffff") -> QWidget:
    widget  = QWidget()
    palette = widget.palette()
    palette.setColor(QPalette.Window, QColor(color))
    widget.setAutoFillBackground(True)
    widget.setPalette(palette)
    return widget


def create_label(text: str, font_size=16, bold=True) -> QLabel:
    label = QLabel(text)
    label.setWordWrap(True)
    label.setAlignment(Qt.AlignCenter)
    font = QFont("Arial", font_size)
    font.setBold(bold)
    label.setFont(font)
    label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
    return label


def create_colored_page(title: str, color: str = "#d0f0c0") -> QWidget:
    page   = create_colored_widget(color)
    layout = QVBoxLayout()
    layout.setAlignment(Qt.AlignCenter)
    layout.addWidget(create_label(title, font_size=20))
    layout.addSpacing(20)
    layout.addWidget(create_answer_input())
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
    layout.setAlignment(Qt.AlignTop)
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
        btn.setFont(QFont("Arial", 14))
        btn.setProperty("class", "footer-button")
        btn.setAccessibleName(name)
        if callbacks and name in callbacks:
            btn.clicked.connect(callbacks[name])
        layout.addWidget(btn)

    footer.setLayout(layout)
    return footer


def create_main_footer_buttons(self):
    buttons    = ["Back to Menu", "Upload", "Settings"]
    translated = {tr(b): b for b in buttons}

    footer = create_footer_buttons(
        list(translated.keys()),
        callbacks={
            tr("Back to Menu"): self.back_to_main_menu,
            tr("Upload"):       self.handle_upload,
            tr("Settings"):     self.handle_settings,
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
    validator = QRegExpValidator(QRegExp(r"-?\d*\.?\d*"))
    input_box.setValidator(validator)
    return input_box


def wrap_center(widget):
    container = QWidget()
    layout    = QHBoxLayout()
    layout.addStretch()
    layout.addWidget(widget)
    layout.addStretch()
    container.setLayout(layout)
    return container


def setup_exit_handling(window, require_confirmation=False):
    def check_and_close(event=None):
        if require_confirmation:
            msg_box = QMessageBox(window)
            msg_box.setWindowTitle(tr("Exit Application"))
            msg_box.setText(tr("Are you sure you want to exit?"))
            yes_btn = msg_box.addButton(tr("Yes"), QMessageBox.YesRole)
            no_btn  = msg_box.addButton(tr("No"),  QMessageBox.NoRole)
            msg_box.setDefaultButton(no_btn)
            msg_box.exec_()
            if msg_box.clickedButton() == yes_btn:
                if event: event.accept()
                else:     QApplication.quit()
            else:
                if event: event.ignore()
        else:
            if event: event.accept()
            else:     QApplication.quit()

    if hasattr(window, "quit_shortcut"):
        window.quit_shortcut.setParent(None)

    window.quit_shortcut = QShortcut(QKeySequence("Ctrl+Q"), window)
    window.quit_shortcut.setContext(Qt.ApplicationShortcut)
    window.quit_shortcut.activated.connect(lambda: check_and_close(event=None))
    window.closeEvent = check_and_close


# ---------------------------------------------------------------------------
# QuestionWidget
# ---------------------------------------------------------------------------

class QuestionWidget(QWidget):
    def __init__(self, processor, window=None, next_question_callback=None, tts=None):
        super().__init__()
        self.setAccessibleName("")
        self.setAccessibleDescription("")
        self.processor              = processor
        self.answer                 = None
        self.start_time             = time()
        self.next_question_callback = next_question_callback
        self.layout                 = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)
        self.main_window   = window
        self.setProperty("theme", window.current_theme)
        self.tts           = tts if tts else TextToSpeech()
        self._question_count = 0
        self.is_bell_mode  = (processor.questionType.lower() == "bellring")
        self.bell_press_count = 0
        self._active       = True
        self.init_ui()

    def init_ui(self):
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setProperty("class", "question-label")
        self.label.setWordWrap(True)
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        if self.is_bell_mode:
            self.input_box    = None
            self.bell_button  = QPushButton("")
            self.bell_button.setIcon(QIcon("images/bell.png"))
            self.bell_button.setIconSize(QSize(128, 128))
            self.bell_button.setMinimumSize(150, 150)
            self.bell_button.setFlat(True)
            self.bell_button.setStyleSheet("border: none; background: transparent;")
            self.bell_button.clicked.connect(self._on_bell_pressed)

            self.bell_pause_timer = QTimer(self)
            self.bell_pause_timer.setSingleShot(True)
            self.bell_pause_timer.setInterval(1500)
            self.bell_pause_timer.timeout.connect(self._evaluate_bell_answer)
        else:
            self.bell_button      = None
            self.bell_pause_timer = None
            self.input_box        = create_answer_input()
            self.input_box.setPlaceholderText("")
            self.input_box.returnPressed.connect(self.check_answer)

        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setFont(QFont("Arial", 46))

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
        self.gif_feedback_label.setAccessibleName("")
        self.gif_feedback_label.setAccessibleDescription("")
        self.layout.addWidget(self.gif_feedback_label, alignment=Qt.AlignCenter)

        self.load_new_question()

    def update_scaling(self, scale):
        if hasattr(self, 'gif_feedback_label') and self.gif_feedback_label:
            sz = min(max(150, int(220 * scale)), 450)
            self.gif_feedback_label.setFixedSize(sz, sz)

        if hasattr(self, 'bell_button') and self.bell_button:
            sz = int(140 * scale)
            self.bell_button.setMinimumSize(sz, sz)
            self.bell_button.setIconSize(QSize(sz - 18, sz - 18))
        elif hasattr(self, 'input_box') and self.input_box:
            self.input_box.setFixedHeight(int(55 * scale))
            self.input_box.setMinimumWidth(int(380 * scale))

        if hasattr(self, 'top_spacer'):
            self.top_spacer.changeSize(20, int(40 * scale), QSizePolicy.Minimum, QSizePolicy.Expanding)
        if hasattr(self, 'mid_spacer'):
            self.mid_spacer.changeSize(20, int(40 * scale), QSizePolicy.Minimum, QSizePolicy.Expanding)
        if hasattr(self, 'input_spacing_item'):
            self.input_spacing_item.changeSize(20, int(25 * scale), QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.layout.invalidate()

    def show_feedback_gif(self, sound_filename):
        gif_name = (
            f"question-{random.choice([1, 2])}.gif"
            if sound_filename == "question"
            else sound_filename.replace(".mp3", ".gif")
        )
        movie = QMovie(f"images/{gif_name}")
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
        if self.is_bell_mode:
            if self.bell_button and not self.bell_button.hasFocus():
                self.bell_button.setFocus()
        elif self.input_box and not self.input_box.hasFocus():
            self.input_box.setFocus()

    def load_new_question(self):
        if hasattr(self, "gif_feedback_label"):
            self.hide_feedback_gif()

        question_text, self.answer = self.processor.get_questions()
        self._active    = True
        
        self.start_time = None
        self.replay_count = 0

        app_tts_active = (
            self.main_window
            and not self.main_window.is_muted
            and self.processor.questionType.lower() != "bellring"
        )

        delay_ms = 0
        if app_tts_active and hasattr(self, 'tts'):
            tts_text = f"{question_text}. {tr('Type your answer')}"
            
            # Accessibility Timer Fix: Time is len(text) * 70ms + 500ms + 1000ms cognitive buffer
            delay_ms = len(tts_text) * 70 + 1500
            
            if self._question_count == 0:
                QTimer.singleShot(10, lambda: self.tts.speak(tts_text))
            else:
                self.tts.speak(tts_text)

        if delay_ms > 0:
            QTimer.singleShot(delay_ms, self._init_start_time)
        else:
            self._init_start_time()

        text_len = len(question_text)
        if text_len > 140:      self.label.setStyleSheet("font-size: 14pt;")
        elif text_len > 100:    self.label.setStyleSheet("font-size: 16pt;")
        elif text_len > 60:     self.label.setStyleSheet("font-size: 19pt;")
        else:                   self.label.setStyleSheet("")

        self.label.setText(question_text)

        if self.input_box:
            self.input_box.clear()
        self.result_label.setText("")
        self.show_feedback_gif("question")

        if self.is_bell_mode:
            self.bell_press_count = 0
            if self.bell_pause_timer and self.bell_pause_timer.isActive():
                self.bell_pause_timer.stop()

        if self.processor.questionType.lower() == "bellring":
            delay = 500 if self._question_count == 0 else 100
            QTimer.singleShot(delay, lambda: self.play_bell_question_sequence(question_text))

        if self.is_bell_mode:
            QTimer.singleShot(100, lambda: self.bell_button.setFocus(Qt.OtherFocusReason))
        elif self.input_box:
            QTimer.singleShot(100, lambda: self.input_box.setFocus(Qt.OtherFocusReason))

        self._question_count += 1

    def play_bell_sounds(self, count):
        if not hasattr(self, "bell_timer"):
            self.bell_timer = QTimer(self)
            self.bell_timer.timeout.connect(self.do_ring)
        self.current_ring  = 0
        self.total_rings   = count
        self.bell_timer.start(700)

    def stop_all_activity(self):
        self._active = False
        for attr in ("bell_timer", "bell_seq_timer", "seq_timer"):
            t = getattr(self, attr, None)
            if t:
                if t.isActive():
                    t.stop()
                t.deleteLater()
                setattr(self, attr, None)
                
        if hasattr(self, "bell_pause_timer") and self.bell_pause_timer:
            if self.bell_pause_timer.isActive():
                self.bell_pause_timer.stop()

    def do_ring(self):
        if self.current_ring < self.total_rings:
            QSound.play("sounds/click-button.wav")
            self.current_ring += 1
        else:
            self.bell_timer.stop()

    def _init_start_time(self):
        if self._active:
            self.start_time = time()

    def increment_replay(self):
        self.replay_count += 1

    # ── Answer checking ──────────────────────────────────────────────────

    def check_answer(self):
        from language.language import tr
        self.stop_all_activity()
        self._active = True

        if not self.input_box:
            return

        user_input = self.input_box.text().strip()
        elapsed    = time() - self.start_time if getattr(self, 'start_time', None) else 0
        
        try:
            result = self.processor.submit_answer(user_input, self.answer, elapsed, self.replay_count)
        except TypeError:
            result = self.processor.submit_answer(user_input, self.answer, elapsed)

        if not result["valid"]:
            msg = tr("Please enter a valid number.")
            self.result_label.setText(msg)
            self.result_label.setAccessibleName(msg)
            return

        correct = result["correct"]
        self._last_result = {
            'correct': correct, 'elapsed': elapsed,
            'skill':   self.processor.questionType,
            'replay_count': getattr(self, 'replay_count', 0)
        }

        audio_on = self.main_window and not self.main_window.is_muted

        if correct:
            if hasattr(self, 'tts'): self.tts.stop()

            is_game = hasattr(self.main_window, 'game_active') and self.main_window.game_active
            if is_game and hasattr(self.main_window, 'time_remaining'):
                self.main_window.time_remaining += 3
                if hasattr(self.main_window, '_update_timer_bar'):
                    self.main_window._update_timer_bar()

            sound_index  = random.randint(1, 3)
            time_offset  = len(self.label.text()) // 30

            feedback_tiers = [
                (5  + time_offset, "Excellent", "🌟", "excellent"),
                (10 + time_offset, "Very Good",  "👏", "very-good"),
                (15 + time_offset, "Good",        "👍", "good"),
                (20 + time_offset, "Not Bad",     "👌", "not-bad"),
                (float('inf'),     "Okay",         "🙂", "okay"),
            ]

            feedback_key = "Okay"; emoji = "🙂"; sound_file = f"okay-{sound_index}.mp3"
            for limit, key, emj, prefix in feedback_tiers:
                if elapsed < limit:
                    feedback_key = key; emoji = emj
                    sound_file   = f"{prefix}-{sound_index}.mp3"
                    break

            clean_feedback = tr(feedback_key)
            self.result_label.setText(
                f'<span style="font-size:16pt;">{emoji} {clean_feedback}</span>'
            )
            self.result_label.setAccessibleName(f"{tr('Correct!')} {clean_feedback}")

            if audio_on and self.main_window:
                self.main_window.play_sound(sound_file)
                self.show_feedback_gif(sound_file)
                if hasattr(self, 'tts'):
                    QTimer.singleShot(10, lambda t=clean_feedback: self.tts.speak(t))

            self.processor.retry_count = 0
            QTimer.singleShot(2000, self.call_next_question)
            return

        else:
            self.processor.retry_count += 1
            is_game = hasattr(self.main_window, 'game_active') and self.main_window.game_active

            if is_game:
                session = getattr(self.main_window, 'game_session', None)
                if session and not getattr(session, 'recovery_mode', False):
                    if hasattr(self.main_window, 'time_remaining'):
                        self.main_window.time_remaining -= 1
                        if hasattr(self.main_window, '_update_timer_bar'):
                            self.main_window._update_timer_bar()
                if audio_on and self.main_window:
                    self.main_window.play_sound("wrong-anwser-1.mp3")
                if hasattr(self.main_window, '_update_timer_bar'):
                    self.main_window._update_timer_bar()
                QTimer.singleShot(300, self.call_next_question)
                return
            else:
                if self.processor.retry_count >= 2:
                    self.result_label.setText(
                        f'<span style="font-size:16pt;">{tr("Let\'s try another one!")}</span>'
                    )
                    QTimer.singleShot(2000, self.call_next_question)
                    return

            try_again = tr("Try Again.")
            self.result_label.setText(f'<span style="font-size:16pt;">{try_again}</span>')
            self.result_label.setAccessibleName(f"{tr('Incorrect.')} {try_again}")

            if audio_on:
                si = random.randint(1, 2)
                sf = (
                    f"wrong-anwser-{si}.mp3"
                    if self.processor.retry_count == 1
                    else f"wrong-anwser-repeted-{si}.mp3"
                )
                self.main_window.play_sound(sf)
                self.show_feedback_gif(sf)
                if hasattr(self, 'tts'):
                    QTimer.singleShot(300, lambda t=try_again: self.tts.speak(t))

            if not self.input_box.hasFocus():
                self.input_box.setFocus()

    def call_next_question(self):
        if not self._active:
            return
        if self.next_question_callback:
            self.next_question_callback()
        else:
            self.load_new_question()

    # ── Bell Ring sequence ───────────────────────────────────────────────

    def play_bell_question_sequence(self, question_text):
        if not self._active:
            return
        self.stop_all_activity()
        self._active = True

        import re
        match = re.search(r'(\d+)\s*([+\-*/×xX])\s*(\d+)', question_text)
        if not match:
            if hasattr(self, 'tts') and self.tts:
                self.tts.speak(question_text)
            return

        num1 = int(match.group(1)); op_char = match.group(2); num2 = int(match.group(3))
        op_map = {
            '+': "Addition",    '-': "Subtraction",
            '*': "Multiplication", '×': "Multiplication",
            'x': "Multiplication", 'X': "Multiplication",
            '/': "Division",    '÷': "Division"
        }
        self.seq_op_text = op_map.get(op_char, "Operation")
        self.seq_num2    = num2
        self.play_bells_with_callback(num1, self._seq_phase_2_speak_op)

    def _seq_phase_2_speak_op(self):
        if not self._active: return
        if hasattr(self, 'tts') and self.tts:
            self.tts.speak(self.seq_op_text)
        self.seq_timer = QTimer(self)
        self.seq_timer.setSingleShot(True)
        self.seq_timer.timeout.connect(self._seq_phase_3_second_operand)
        self.seq_timer.start(1500)

    def _seq_phase_3_second_operand(self):
        if not self._active: return
        self.play_bells_with_callback(self.seq_num2, self._seq_phase_4_done)

    def _seq_phase_4_done(self):
        if not self._active: return
        if self.is_bell_mode:
            if hasattr(self, 'tts') and self.tts and self.main_window and not self.main_window.is_muted:
                QTimer.singleShot(300, lambda: self.tts.speak("Now ring your answer"))
            QTimer.singleShot(500, lambda: self.bell_button.setFocus(Qt.OtherFocusReason))

    def play_bells_with_callback(self, count, callback):
        t = getattr(self, "bell_seq_timer", None)
        if t and t.isActive():
            t.stop()
        if count <= 0:
            if callback: callback()
            return
        self.bell_seq_counter  = 0
        self.bell_seq_total    = count
        self.bell_seq_callback = callback
        self.bell_seq_timer    = QTimer(self)
        self.bell_seq_timer.timeout.connect(self._on_bell_seq_tick)
        self.bell_seq_timer.start(600)
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

    def _on_bell_pressed(self):
        self.bell_press_count += 1
        self._shake_bell()
        if self.main_window and not self.main_window.is_muted:
            self.main_window.play_sound("BellRing.mp3")
        if self.bell_pause_timer:
            self.bell_pause_timer.stop()
            self.bell_pause_timer.start(1500)

    def _shake_bell(self):
        if not self.bell_button: return
        origin     = self.bell_button.pos()
        anim_group = QSequentialAnimationGroup(self)
        for dx in [4, -8, 6, -4, 2, 0]:
            anim = QPropertyAnimation(self.bell_button, b"pos")
            anim.setDuration(35)
            anim.setEndValue(QPoint(origin.x() + dx, origin.y()))
            anim_group.addAnimation(anim)
        anim_group.start()
        self._shake_anim = anim_group

    def _evaluate_bell_answer(self):
        count = self.bell_press_count
        self.bell_press_count = 0

        try:    correct_answer = int(self.answer)
        except: correct_answer = -1

        elapsed    = time() - self.start_time if getattr(self, 'start_time', None) else 0
        is_correct = (count == correct_answer)
        self._last_result = {
            'correct': is_correct, 'elapsed': elapsed,
            'skill':   self.processor.questionType,
            'replay_count': getattr(self, 'replay_count', 0)
        }

        audio_on = self.main_window and not self.main_window.is_muted

        if is_correct:
            if hasattr(self, 'tts'): self.tts.stop()

            is_game = hasattr(self.main_window, 'game_active') and self.main_window.game_active
            if is_game and hasattr(self.main_window, 'time_remaining'):
                self.main_window.time_remaining += 3
                if hasattr(self.main_window, '_update_timer_bar'):
                    self.main_window._update_timer_bar()

            sound_index = random.randint(1, 3)
            if elapsed < 5:   fb = "🌟 Excellent"
            elif elapsed < 10: fb = "👏 Very Good"
            elif elapsed < 15: fb = "👍 Good"
            elif elapsed < 20: fb = "👌 Not Bad"
            else:              fb = "🙂 Okay"

            self.result_label.setText(f'<span style="font-size:16pt;">{fb}</span>')
            clean = fb.replace("🌟","").replace("👏","").replace("👍","").replace("👌","").replace("🙂","").strip()
            self.result_label.setAccessibleName(f"Correct! {clean}")

            if audio_on and self.main_window:
                if elapsed < 5:   sf = f"excellent-{sound_index}.mp3"
                elif elapsed < 10: sf = f"very-good-{sound_index}.mp3"
                elif elapsed < 15: sf = f"good-{sound_index}.mp3"
                elif elapsed < 20: sf = f"not-bad-{sound_index}.mp3"
                else:              sf = f"okay-{sound_index}.mp3"
                self.main_window.play_sound(sf)
                self.show_feedback_gif(sf)
                if hasattr(self, 'tts'):
                    QTimer.singleShot(300, lambda t=clean: self.tts.speak(t))

            self.processor.retry_count = 0
            QTimer.singleShot(2000, self.call_next_question)

        else:
            self.processor.retry_count += 1
            from language.language import tr

            is_game = hasattr(self.main_window, 'game_active') and self.main_window.game_active
            if is_game:
                session = getattr(self.main_window, 'game_session', None)
                if session and not getattr(session, 'recovery_mode', False):
                    if hasattr(self.main_window, 'time_remaining'):
                        self.main_window.time_remaining -= 1
                        if hasattr(self.main_window, '_update_timer_bar'):
                            self.main_window._update_timer_bar()
                if audio_on and self.main_window:
                    self.main_window.play_sound("wrong-anwser-1.mp3")
                self.call_next_question()
                return
            else:
                if getattr(self.processor, 'retry_count', 0) >= 2:
                    self.result_label.setText(
                        f'<span style="font-size:16pt;">{tr("Let\'s try another one!")}</span>'
                    )
                    QTimer.singleShot(2000, self.call_next_question)
                    return

            self.result_label.setText('<span style="font-size:16pt;">Try Again.</span>')
            self.result_label.setAccessibleName("Incorrect. Try Again.")

            if audio_on and self.main_window:
                si = random.randint(1, 2)
                sf = (
                    f"wrong-anwser-{si}.mp3"
                    if self.processor.retry_count == 1
                    else f"wrong-anwser-repeted-{si}.mp3"
                )
                self.main_window.play_sound(sf)
                self.show_feedback_gif(sf)
                if hasattr(self, 'tts'):
                    QTimer.singleShot(300, lambda: self.tts.speak("Try Again"))

            if self.bell_button and not self.bell_button.hasFocus():
                self.bell_button.setFocus()


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def create_dynamic_question_ui(section_name, difficulty_index, back_callback,
                                main_window=None, back_to_operations_callback=None, tts=None):
    container = QWidget()
    container.setAccessibleName("")
    container.setAccessibleDescription("")
    layout = QVBoxLayout()
    layout.setAlignment(Qt.AlignTop)
    container.setLayout(layout)

    if section_name.lower() == "bellring":
        print(f"[BellRing] Overriding difficulty {difficulty_index} -> 1")
        difficulty_index = 1

    processor = QuestionProcessor(section_name, difficulty_index)
    processor.process_file()
    layout.addWidget(QuestionWidget(processor, main_window, tts=tts))
    apply_theme(container, main_window.current_theme)
    return container


def apply_theme(widget, theme):
    if not widget:
        return
    widget.setProperty("theme", theme)
    widget.style().unpolish(widget)
    widget.style().polish(widget)
    widget.update()
    for child in widget.findChildren(QWidget):
        child.setProperty("theme", theme)
        child.style().unpolish(child)
        child.style().polish(child)
        child.update()


# ---------------------------------------------------------------------------
# SettingsDialog
# ---------------------------------------------------------------------------

class SettingsDialog(QDialog):
    def __init__(self, parent=None, initial_difficulty=1, main_window=None):
        super().__init__(parent)
        self.main_window      = main_window
        self.updated_language = main_window.language if main_window else "English"

        self.setWindowTitle(tr("Settings"))
        self.setMinimumSize(400, 280)

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
        self.difficulty_slider.valueChanged.connect(self.update_difficulty_label)

        self.difficulty_label = create_label(self.get_localized_difficulty(initial_difficulty), font_size=12)
        self.difficulty_label.setProperty("class", "difficulty-label")
        self.difficulty_label.setProperty("theme", parent.current_theme)
        self.difficulty_label.setAccessibleName(" ")

        QTimer.singleShot(250, lambda: self.difficulty_slider.setFocus())
        self.setProperty("theme", parent.current_theme)

        self.language_reset_btn = QPushButton(tr("Reset Language"))
        self.language_reset_btn.setFixedHeight(30)
        self.language_reset_btn.clicked.connect(self.handle_reset_language)
        self.language_reset_btn.setAccessibleName(tr("Reset Language"))
        self.language_reset_btn.setAccessibleDescription(
            tr("Clear saved language preference and choose a new language")
        )

        button_box = QDialogButtonBox()
        ok_btn     = button_box.addButton(tr("OK"),     QDialogButtonBox.AcceptRole)
        cancel_btn = button_box.addButton(tr("Cancel"), QDialogButtonBox.RejectRole)
        button_box.accepted.connect(self.accept_settings)
        button_box.rejected.connect(self.reject)
        ok_btn.setAccessibleName(tr("OK — Apply settings"))
        cancel_btn.setAccessibleName(tr("Cancel — Discard changes"))

        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        diff_header = QLabel(tr("Select Difficulty:"))
        diff_header.setProperty("class", "difficulty-label")
        diff_header.setProperty("theme", parent.current_theme)
        diff_header.setAccessibleName(
            tr("Select Difficulty. Use left or right arrow keys to select difficulty level.")
        )
        diff_header.setBuddy(self.difficulty_slider)

        layout.addWidget(diff_header)
        layout.addWidget(self.difficulty_slider)
        layout.addWidget(self.difficulty_label)
        layout.addWidget(self.language_reset_btn)

        extra = QHBoxLayout()
        self.help_button  = QPushButton(tr("Help"))
        self.about_button = QPushButton(tr("About"))
        for btn in [self.help_button, self.about_button]:
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            btn.setFixedHeight(30)
        self.help_button.setAccessibleName(tr("Help"))
        self.about_button.setAccessibleName(tr("About"))
        extra.addWidget(self.help_button)
        extra.addWidget(self.about_button)
        layout.addLayout(extra)

        layout.addStretch()
        layout.addWidget(button_box)
        self.setLayout(layout)

        QWidget.setTabOrder(self.difficulty_slider, self.language_reset_btn)
        QWidget.setTabOrder(self.language_reset_btn, self.help_button)
        QWidget.setTabOrder(self.help_button, self.about_button)
        QWidget.setTabOrder(self.about_button, ok_btn)
        QWidget.setTabOrder(ok_btn, cancel_btn)

    def get_localized_difficulty(self, index):
        eng = DIFFICULTY_LEVELS[index]
        if self.updated_language == "हिंदी":
            return {"Simple":"सरल","Easy":"आसान","Medium":"मध्यम",
                    "Hard":"कठिन","Challenging":"चुनौतीपूर्ण"}.get(eng, eng)
        return eng

    def update_difficulty_label(self, index):
        level = self.get_localized_difficulty(index)
        self.difficulty_label.setText(level)
        self.difficulty_label.setAccessibleName(" ")
        if self.main_window and hasattr(self.main_window, 'tts') and not self.main_window.is_muted:
            self.main_window.tts.stop()
            QTimer.singleShot(200, lambda: self.main_window.tts.speak(level))

    def handle_reset_language(self):
        from main import RootWindow
        from language.language import clear_remember_language, set_language
        clear_remember_language()
        dialog = RootWindow(minimal=True)
        if dialog.exec_() == QDialog.Accepted:
            new_lang = dialog.language_combo.currentText()
            set_language(new_lang)
            self.updated_language = new_lang
            QMessageBox.information(
                self, tr("Language Changed"),
                tr("Language changed to {new_lang}. The app will now reload.").format(new_lang=new_lang)
            )
            if self.main_window:
                self.main_window.refresh_ui(new_lang)
            self.close()

    def accept_settings(self):
        settings.set_difficulty(self.difficulty_slider.value())
        settings.set_language(self.updated_language)
        self.accept()

    def get_difficulty_index(self):
        return self.difficulty_slider.value()

    def get_selected_language(self):
        return self.updated_language


# ---------------------------------------------------------------------------
# GameReportWidget  —  structured breakdown + full summary
# ---------------------------------------------------------------------------

class GameReportWidget(QWidget):
    def __init__(self, session, window, tts):
        super().__init__()
        self.session     = session
        self.main_window = window
        self.tts         = tts
        self.setAccessibleName("")
        self.setAccessibleDescription("")

        avg_skill = sum(session.skill_scores.values()) / max(len(session.skill_scores), 1)
        self.can_advance = (
            (getattr(session, 'level_completed', False) or (avg_skill >= 65 and session.questions_answered >= 10))
            and session.difficulty_index < getattr(session, 'max_level', 3)
        )

        self.breakdown_text = session.generate_breakdown()
        self.summary_text   = session.generate_summary()

        self.init_ui()
        self._speak_report()

    def init_ui(self):
        from language.language import tr
        levels = ["Easy", "Medium", "Hard", "Extra Hard"]

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(14)
        layout.setContentsMargins(30, 20, 30, 20)
        self.setLayout(layout)

        # Title
        title = QLabel(tr("Session Complete!"))
        title.setAlignment(Qt.AlignCenter)
        title.setProperty("class", "main-title")
        layout.addWidget(title)

        # Per-skill breakdown (compact, one line, alphabetical)
        breakdown_label = QLabel(self.breakdown_text)
        breakdown_label.setAlignment(Qt.AlignCenter)
        breakdown_label.setWordWrap(True)
        breakdown_label.setProperty("class", "subtitle")
        breakdown_label.setAccessibleName(self.breakdown_text)
        layout.addWidget(breakdown_label)

        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setFrameShadow(QFrame.Sunken)
        layout.addWidget(divider)

        # Narrative summary — ALL strengths and ALL weaknesses
        summary_label = QLabel(self.summary_text)
        summary_label.setAlignment(Qt.AlignCenter)
        summary_label.setWordWrap(True)
        summary_label.setProperty("class", "subtitle")
        summary_label.setAccessibleName(self.summary_text)
        layout.addWidget(summary_label)

        # Session info
        cur_level  = levels[self.session.starting_difficulty] if self.session.starting_difficulty < len(levels) else ""
        info_label = QLabel(
            f"{self.session.questions_answered} {tr('questions answered')}  ·  "
            f"{tr('Level')}: {tr(cur_level)}"
        )
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setProperty("class", "subtitle")
        layout.addWidget(info_label)

        layout.addSpacing(6)

        # Action buttons
        btn_row = QHBoxLayout()
        btn_row.setAlignment(Qt.AlignCenter)
        btn_row.setSpacing(20)

        current_name = tr(cur_level)

        if self.can_advance:
            next_name        = tr(levels[self.session.difficulty_index + 1])
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

    def _speak_report(self):
        from language.language import tr
        speak_text   = f"{self.breakdown_text}. {self.summary_text}"
        est_ms       = len(speak_text) * 65
        choice_text  = tr("Ready for the next level?") if self.can_advance else tr("Play again?")

        QTimer.singleShot(800,          lambda: self.tts.speak(speak_text))
        QTimer.singleShot(800 + est_ms, lambda: self.tts.speak(choice_text))

        primary = self.primary_btn if self.can_advance else self.replay_btn
        QTimer.singleShot(
            800 + est_ms + len(choice_text) * 65,
            lambda: primary.setFocus()
        )

    def _go_next_level(self):
        self.tts.stop()
        self.main_window.load_game_questions(self.session.starting_difficulty + 2)

    def _replay_level(self):
        self.tts.stop()
        self.main_window.load_game_questions(self.session.starting_difficulty + 1)