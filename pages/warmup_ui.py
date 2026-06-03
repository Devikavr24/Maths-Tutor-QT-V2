"""pages/warmup_ui.py

Three QWidget screens for the Warmup Match flow:
  WarmupIntroWidget       — intro / explanation screen
  WarmupQuestionWidget    — question presenter (all 13 steps in one widget)
  WarmupRankingWidget     — post-warmup ranked results screen
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QProgressBar, QSizePolicy, QScrollArea, QFrame,
    QSpacerItem
)
from PyQt5.QtCore import Qt, QTimer, QRegExp
from PyQt5.QtGui import QFont, QRegExpValidator
from time import time

from question.warmup import (
    SCORE_INFO, AUTO_SKIP_SECONDS, WarmupSession
)
# from language.language import tr
import language.language as lang_config


# ---------------------------------------------------------------------------
# Colour palette (score → hex) — used on ranking rows
# ---------------------------------------------------------------------------
SCORE_COLOURS = {1.0: "#27AE60", 0.5: "#D4AC0D", 0.2: "#E67E22", 0.0: "#95A5A6"}


# ---------------------------------------------------------------------------
# WarmupIntroWidget
# ---------------------------------------------------------------------------

class WarmupIntroWidget(QWidget):
    """
    Intro/explanation screen shown before the warmup questions begin.
    Calls on_begin() when the user presses "Begin Warmup".
    """

    def __init__(self, on_begin, window, tts):
        super().__init__()
        self.on_begin   = on_begin
        self.window     = window
        self.tts        = tts
        self.setAccessibleName(_("Warmup Match Introduction"))
        self._init_ui()
        # self._speak_intro()

    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(18)
        layout.setContentsMargins(50, 30, 50, 30)
        self.setLayout(layout)

        layout.addStretch()

        title = QLabel("🏁 " + _("Warmup Match"))
        title.setAlignment(Qt.AlignCenter)
        title.setProperty("class", "main-title")
        title.setAccessibleName(_("Warmup Match"))
        layout.addWidget(title)

        layout.addSpacing(10)

        current_lang = getattr(lang_config, 'selected_language', 'English')
        if current_lang == "മലയാളം":
            desc_text = (
                "സ്വാഗതം! യഥാർത്ഥ ഗെയിം ആരംഭിക്കുന്നതിന് മുൻപ്, നിങ്ങളുടെ കഴിവുകൾ മനസ്സിലാക്കാൻ നമുക്കൊരു ചെറിയ വാംഅപ്പ് മത്സരം കളിക്കാം.\n\n"
                "ഏറ്റവും എളുപ്പമുള്ളതിൽ തുടങ്ങി വ്യത്യസ്ത ചോദ്യ തരങ്ങളിൽ നിന്നുള്ള ഓരോ ചോദ്യങ്ങൾക്ക് നിങ്ങൾ ഉത്തരം നൽകേണ്ടതുണ്ട്. ചോദ്യം ഉച്ചത്തിൽ വായിച്ചതിന് ശേഷം നിങ്ങളുടെ വേഗതയും കൃത്യതയും അളക്കപ്പെടുന്നു.\n\n"
                "കൂടുതൽ ചോദ്യങ്ങൾ തെറ്റിക്കുകയോ ഒഴിവാക്കുകയോ ചെയ്താൽ മാത്രമേ വാംഅപ്പ് നേരത്തെ അവസാനിക്കുകയുള്ളൂ."
            )
        else:
            desc_text = (
                "Welcome! Before we begin the real game, let's do a quick "
                "Warmup Match so we can understand your strengths.\n\n"
                "You will answer one question from each of the different question types, "
                "starting from the easiest. Your speed and accuracy are measured "
                "after the question is read aloud.\n\n"
                "The warmup ends early only if you miss or skip too many questions."
            )

        desc = QLabel(desc_text)
        desc.setAlignment(Qt.AlignCenter)
        desc.setWordWrap(True)
        desc.setProperty("class", "subtitle")
        desc.setMaximumWidth(560)
        # desc.setAccessibleDescription("")
        layout.addWidget(desc, alignment=Qt.AlignCenter)

        layout.addSpacing(20)

        # Info row
        info_row = QHBoxLayout()
        info_row.setAlignment(Qt.AlignCenter)
        info_row.setSpacing(30)
        for icon, label_text in [("⏱️", _("Speed matters")), ("🎯", _("14 question types")), ("📊", _("Ranked results"))]:
            col = QVBoxLayout()
            col.setAlignment(Qt.AlignCenter)
            ico = QLabel(icon)
            ico.setAlignment(Qt.AlignCenter)
            ico.setFont(QFont("Arial", 22))
            ico.setAccessibleName("")
            lbl = QLabel(label_text)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setProperty("class", "subtitle")
            col.addWidget(ico)
            col.addWidget(lbl)
            w = QWidget()
            w.setLayout(col)
            info_row.addWidget(w)
        layout.addLayout(info_row)

        layout.addSpacing(25)

        self.begin_btn = QPushButton("🚀  " + _("Begin Warmup"))
        self.begin_btn.setMinimumSize(260, 70)
        self.begin_btn.setProperty("class", "menu-button")
        self.begin_btn.setAccessibleName(_("Begin Warmup"))
        self.begin_btn.setAccessibleDescription(
            "Welcome! Before we begin the real game, let's do a quick Warmup Match so we can understand your strengths"
            "You will answer one question from each of the different question types starting from the easiest. Press Sapce key to Start"
        )
        self.begin_btn.clicked.connect(self._on_begin)
        layout.addWidget(self.begin_btn, alignment=Qt.AlignCenter)

        layout.addStretch()

        QTimer.singleShot(200, self.begin_btn.setFocus)

    def _speak_intro(self):
        if self.window and not self.window.is_muted and self.tts:
            current_lang = getattr(lang_config, 'selected_language', 'English')
            intros = {
                "മലയാളം": "വാംഅപ്പ് മത്സരത്തിലേക്ക് സ്വാഗതം! ഓരോ ചോദ്യ തരം പരിശോധിച്ചു നിങ്ങളുടെ കഴിവുകൾ ഞങ്ങൾ വിലയിരുത്തും. തയ്യാറാകുമ്പോൾ വാംഅപ്പ് ആരംഭിക്കുക ക്ലിക്ക് ചെയ്യുക.",
                "हिंदी": "वार्मअप मैच में आपका स्वागत है! हम प्रत्येक प्रकार के प्रश्न पूछकर आपकी ताकत का आकलन करेंगे। जब आप तैयार हों तो वार्मअप शुरू करें बटन दबाएं।",
                "தமிழ்": "வார்ம்அப் போட்டிக்கு வரவேற்கிறோம்! ஒவ்வொரு கேள்வி வகையையும் கேட்டு உங்கள் திறமைகளை நாங்கள் மதிப்பீடு செய்வோம். நீங்கள் தயாராக இருக்கும்போது வார்ம்அப் தொடங்கவும் பொத்தானை அழுத்தவும்.",
                "عربي": "مرحبًا بك في المباراة التجريبية! سنقوم بتقييم نقاط قوتك من خلال طرح سؤال من كل نوع. اضغط على ابدأ الإحماء عندما تكون مستعدًا.",
                "संस्कृत": "वार्मअप क्रीडायां भवतः स्वागतम्! वयं प्रत्येकं प्रकारस्य प्रश्नान् पृष्ट्वा भवतး सामर्थ्यस्य मूल्याङ्कनं करिष्यामः। यदा भवान् सज्जः भवति तदा വാംഅപ്പ് ആരംഭിക്കുക ക്ലിക്ക് ചെയ്യുക।",
                "English": (
                    "Welcome to the Warmup Match! "
                    "We will assess your strengths by asking one question from each type. "
                    "Press Begin Warmup when you are ready."
                )
            }
            msg = intros.get(current_lang, intros["English"])
            # QTimer.singleShot(400, lambda: self.tts.speak(msg))

    def _on_begin(self):
        if self.tts:
            self.tts.stop()
        self.on_begin()

    def cleanup(self):
        if self.tts:
            self.tts.stop()


# ---------------------------------------------------------------------------
# WarmupQuestionWidget
# ---------------------------------------------------------------------------

class WarmupQuestionWidget(QWidget):
    """
    Handles all 13 warmup steps inside a single persistent widget.
    Reloads its own content for each new step without being replaced.
    """

    def __init__(self, session: WarmupSession, window, tts, on_complete):
        super().__init__()
        self.session       = session
        self.window        = window
        self.tts           = tts
        self.on_complete   = on_complete

        self._active              = True
        self._question_start_time = None
        self._current_answer      = None
        self._current_question_text = ""

        # self.setAccessibleName("Warmup Question")
        self._init_ui()
        self._load_current_step()

    def showEvent(self, event):
        super().showEvent(event)
        # Force focus to the silent feedback label the exact moment the screen appears
        if hasattr(self, 'feedback_lbl'):
            self.feedback_lbl.setFocus()

    # ── UI setup ─────────────────────────────────────────────────────────────

    def _init_ui(self):
        root = QVBoxLayout()
        root.setContentsMargins(30, 10, 30, 10)
        root.setSpacing(8)
        self.setLayout(root)

        # Header row: title + step counter
        header = QHBoxLayout()
        warmup_lbl = QLabel("🏁 " + _("Warmup Match"))
        warmup_lbl.setProperty("class", "subtitle")
        warmup_lbl.setAccessibleName("")
        header.addWidget(warmup_lbl, alignment=Qt.AlignLeft)

        self.step_counter_lbl = QLabel("")
        self.step_counter_lbl.setProperty("class", "subtitle")
        self.step_counter_lbl.setAlignment(Qt.AlignRight)
        header.addWidget(self.step_counter_lbl, alignment=Qt.AlignRight)
        root.addLayout(header)
        if hasattr(self.window, "theme_button"):
            self.window.theme_button.hide()
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(self.session.total_steps())
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(10)
        self.progress_bar.setAccessibleName("")
        self.progress_bar.setAccessibleDescription("")
        root.addWidget(self.progress_bar)

        # Question type label
        self.type_lbl = QLabel("")
        self.type_lbl.setAlignment(Qt.AlignCenter)
        self.type_lbl.setProperty("class", "main-title")
        root.addWidget(self.type_lbl)

        root.addStretch(1)

        # Question text
        self.question_lbl = QLabel("")
        self.question_lbl.setAlignment(Qt.AlignCenter)
        self.question_lbl.setWordWrap(True)
        self.question_lbl.setProperty("class", "question-label")
        self.question_lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        root.addWidget(self.question_lbl)

        root.addStretch(1)

        # Auto-skip timer bar
        self.autoskip_bar = QProgressBar()
        self.autoskip_bar.setMinimum(0)
        self.autoskip_bar.setMaximum(AUTO_SKIP_SECONDS)
        self.autoskip_bar.setValue(AUTO_SKIP_SECONDS)
        self.autoskip_bar.setTextVisible(True)
        self.autoskip_bar.setFormat(_("Auto-skip in %vs"))
        self.autoskip_bar.setFixedHeight(18)
        self.autoskip_bar.setVisible(False)
        self.autoskip_bar.setAccessibleName("")
        root.addWidget(self.autoskip_bar)

        # Input row
        input_row = QHBoxLayout()
        input_row.setSpacing(10)
        input_row.setAlignment(Qt.AlignCenter)

        self.input_box = QLineEdit()
        self.input_box.setMinimumSize(220, 55)
        self.input_box.setMaximumWidth(320)
        self.input_box.setAlignment(Qt.AlignCenter)
        self.input_box.setPlaceholderText(_("Enter your answer"))
        self.input_box.setFont(QFont("Arial", 16))
        self.input_box.setProperty("class", "answer-input")
        # self.input_box.setAccessibleName(_("Answer input"))
        validator = QRegExpValidator(QRegExp(r"-?\d*\.?\d*"))
        self.input_box.setValidator(validator)
        self.input_box.returnPressed.connect(self._check_answer)
        input_row.addWidget(self.input_box)

        self.submit_btn = QPushButton("✓  " + _("Submit"))
        self.submit_btn.setMinimumSize(120, 55)
        self.submit_btn.setProperty("class", "menu-button")
        self.submit_btn.setAccessibleName(_("Submit answer"))
        self.submit_btn.clicked.connect(self._check_answer)
        input_row.addWidget(self.submit_btn)

        root.addLayout(input_row)

        root.addSpacing(10)

        # Skip button (always visible, prominent)
        self.skip_btn = QPushButton("⏭  " + _("Skip this question"))
        self.skip_btn.setMinimumSize(200, 48)
        self.skip_btn.setProperty("class", "footer-button")
        self.skip_btn.setFont(QFont("Arial", 13))
        self.skip_btn.setAccessibleName(_("Skip this question"))
        self.skip_btn.setAccessibleDescription(
            _("Skip the current question. Skipped questions score zero.")
        )
        self.skip_btn.clicked.connect(self._on_skip)
        root.addWidget(self.skip_btn, alignment=Qt.AlignCenter)

        # Feedback label
        self.feedback_lbl = QLabel("")
        self.feedback_lbl.setAlignment(Qt.AlignCenter)
        self.feedback_lbl.setFont(QFont("Arial", 22, QFont.Bold))
        self.feedback_lbl.setFixedHeight(50)
        self.feedback_lbl.setFocusPolicy(Qt.StrongFocus)
        self.feedback_lbl.setAccessibleName(" ")
        self.feedback_lbl.setFocus()
        root.addWidget(self.feedback_lbl)

        root.addStretch(1)

        # Timers
        self.autoskip_timer = QTimer(self)
        self.autoskip_timer.setSingleShot(True)
        self.autoskip_timer.setInterval(AUTO_SKIP_SECONDS * 1000)
        self.autoskip_timer.timeout.connect(self._on_autoskip)

        self.autoskip_tick_timer = QTimer(self)
        self.autoskip_tick_timer.setInterval(1000)
        self.autoskip_tick_timer.timeout.connect(self._on_autoskip_tick)

        self._autoskip_remaining = AUTO_SKIP_SECONDS

    # ── Step loading ─────────────────────────────────────────────────────────

    def _load_current_step(self):
        if not self._active:
            return
        if self.session.is_complete():
            self._finish()
            return

        # Stop stale timers
        self.autoskip_timer.stop()
        self.autoskip_tick_timer.stop()
        self.autoskip_bar.setVisible(False)

        step = self.session.current_step()
        step_num = self.session.step_index + 1
        total    = self.session.total_steps()

        # Update progress UI
        self.step_counter_lbl.setText(_("Question {n} / {total}").format(n=step_num, total=total))
        self.progress_bar.setValue(self.session.step_index)
        
        # Localize question type label dynamically
        lbl_text = step["label"]
        parts = lbl_text.split("_")
        if len(parts) == 2:
            digit, operation = parts[0], parts[1].capitalize()
            translated_lbl = f"{digit} {_(operation)}"
        else:
            translated_lbl = _(lbl_text)
        self.type_lbl.setText(translated_lbl)
        self.feedback_lbl.setText("")
        self.feedback_lbl.setFocus()   
        self.input_box.clear()
        self.input_box.setEnabled(False)
        self.submit_btn.setEnabled(True)
        self.skip_btn.setEnabled(True)

        # Build processor and get question
        processor = self.session.get_current_processor()
        if processor is None or (processor.df is not None and processor.df.empty):
            # No data for this step → auto-skip silently
            self.session.skip_question()
            QTimer.singleShot(0, self._load_current_step)
            return

        question_text, self._current_answer = processor.get_questions()
        self._current_question_text = question_text

        # Record question ID used during warmup to prevent repetitions in Game Mode
        if processor.df is not None and "id" in processor.df.columns and 0 <= processor.rowIndex < len(processor.df):
            q_id = processor.df.iloc[processor.rowIndex]["id"]
            if hasattr(self.session, "used_question_ids"):
                self.session.used_question_ids.add(q_id)

        if question_text == "No questions found." or self._current_answer is None:
            self.session.skip_question()
            QTimer.singleShot(0, self._load_current_step)
            return

        # Adjust font size by length
        length = len(question_text)
        if length > 120:
            self.question_lbl.setStyleSheet("font-size: 14pt;")
        elif length > 80:
            self.question_lbl.setStyleSheet("font-size: 18pt;")
        else:
            self.question_lbl.setStyleSheet("")

        self.question_lbl.setText(question_text)

        # TTS + deferred timer start
        self._question_start_time = None
        audio_on = self.window and not self.window.is_muted

        if audio_on and self.tts:
            tts_text = f"{question_text}. {_('Type your answer')}"
            delay_ms = len(tts_text) * 70 + 1500
            self.tts.speak(tts_text)
            QTimer.singleShot(delay_ms, self._on_tts_done)
        else:
            self._on_tts_done()

        

    def _on_tts_done(self):
        if not self._active:
            return
        self._question_start_time = time()
        self._autoskip_remaining  = AUTO_SKIP_SECONDS
        self.autoskip_bar.setValue(AUTO_SKIP_SECONDS)
        self.autoskip_bar.setVisible(True)
        self.autoskip_timer.start()
        self.autoskip_tick_timer.start()
        self.input_box.setEnabled(True)
        QTimer.singleShot(100, self.input_box.setFocus)

    def _on_autoskip_tick(self):
        self._autoskip_remaining = max(0, self._autoskip_remaining - 1)
        self.autoskip_bar.setValue(self._autoskip_remaining)

    # ── Answer handling ──────────────────────────────────────────────────────

    def _check_answer(self):
        if not self._active:
            return
        self._stop_timers()

        user_text = self.input_box.text().strip()
        if not user_text:
            self.input_box.setFocus()
            return

        try:
            user_val    = float(user_text)
            correct_val = float(self._current_answer)
            is_correct  = (user_val == correct_val)
        except (TypeError, ValueError):
            self.feedback_lbl.setText(f'<span style="color:#E74C3C;">✗ {_("Invalid — try again")}</span>')
            self.input_box.setFocus()
            return

        elapsed = (time() - self._question_start_time) if self._question_start_time else 0.0
        score   = self.session.submit_answer(is_correct, elapsed)
        self.feedback_lbl.setFocus()
        self.input_box.setEnabled(False)
        self.submit_btn.setEnabled(False)
        self.skip_btn.setEnabled(False)

        current_lang = getattr(lang_config, 'selected_language', 'English')

        if is_correct:
            emoji, label = SCORE_INFO.get(score, ("✓", ""))
            self.feedback_lbl.setText(
                f'<span style="color:#27AE60; font-size:22pt;">{emoji} {_("Correct!")}  {_(label)}</span>'
            )
            if self.window and not self.window.is_muted:
                import random
                sound_index = random.randint(1, 3)
                if score == 1.0:
                    sound_file = f"excellent-{sound_index}.mp3"
                elif score == 0.5:
                    sound_file = f"good-{sound_index}.mp3"
                elif score == 0.2:
                    sound_file = f"not-bad-{sound_index}.mp3"
                else:
                    sound_file = f"okay-{sound_index}.mp3"
                self.window.play_sound(sound_file)

            # if self.tts and self.window and not self.window.is_muted:
            #     if current_lang == "മലയാളം":
            #         QTimer.singleShot(50, lambda: self.tts.speak(f"ശരിയാണ്! {_(label)}"))
            #     else:
            #         QTimer.singleShot(50, lambda: self.tts.speak(f"Correct! {label}"))
            QTimer.singleShot(1400, self._advance)
        else:
            self.feedback_lbl.setText(
                f'<span style="color:#E74C3C; font-size:22pt;">✗ {_("Wrong — moving on")}</span>'
            )
            self.feedback_lbl.setFocus()
            if self.window and not self.window.is_muted:
                import random
                self.window.play_sound(f"wrong-anwser-{random.randint(1, 3)}.mp3")

            # if self.tts and self.window and not self.window.is_muted:
            #     if current_lang == "മലയാളം":
            #         QTimer.singleShot(50, lambda: self.tts.speak("തെറ്റാണ്."))
            #     else:
            #         QTimer.singleShot(50, lambda: self.tts.speak("Wrong."))
            QTimer.singleShot(1200, self._advance)

    def _on_skip(self):
        if not self._active:
            return
        self._stop_timers()
        self.session.skip_question()
        self.input_box.setEnabled(False)
        self.submit_btn.setEnabled(False)
        self.skip_btn.setEnabled(False)
        self.feedback_lbl.setText(f'<span style="color:#95A5A6; font-size:18pt;">⏭ {_("Skipped")}</span>')
        if self.window and not self.window.is_muted:
            self.window.play_sound("wrong-anwser-1.mp3")
        QTimer.singleShot(800, self._advance)

    def _on_autoskip(self):
        if not self._active:
            return
        self.autoskip_tick_timer.stop()
        self.autoskip_bar.setValue(0)
        self.session.skip_question()
        self.input_box.setEnabled(False)
        self.submit_btn.setEnabled(False)
        self.skip_btn.setEnabled(False)
        self.feedback_lbl.setText(f'<span style="color:#95A5A6; font-size:18pt;">⏱ {_("Time out — auto-skipped")}</span>')
        if self.window and not self.window.is_muted:
            self.window.play_sound("wrong-anwser-1.mp3")
        QTimer.singleShot(1000, self._advance)

    def _advance(self):
        if not self._active:
            return
        if self.session.is_complete():
            self._finish()
        else:
            self._load_current_step()

    def _finish(self):
        self._active = False
        self._stop_timers()
        if hasattr(self.window, "theme_button"):
            self.window.theme_button.show()
        self.on_complete()

    # ── Utilities ────────────────────────────────────────────────────────────

    def _stop_timers(self):
        self.autoskip_timer.stop()
        self.autoskip_tick_timer.stop()
        self.autoskip_bar.setVisible(False)

    def cleanup(self):
        self._active = False
        self._stop_timers()
        if hasattr(self.window, "theme_button"):
            self.window.theme_button.show()
        if self.tts:
            self.tts.stop()


# ---------------------------------------------------------------------------
# WarmupRankingWidget
# ---------------------------------------------------------------------------

class WarmupRankingWidget(QWidget):
    """
    Post-warmup screen that displays ranked results and offers a
    "Continue to Game Mode" button.
    """

    def __init__(self, session: WarmupSession, window, tts, on_continue):
        super().__init__()
        self.session     = session
        self.window      = window
        self.tts         = tts
        self.on_continue = on_continue
        self.setAccessibleName(_("Warmup Results"))
        self._init_ui()
        self._speak_results()

    def _init_ui(self):
        root = QVBoxLayout()
        root.setContentsMargins(40, 20, 40, 20)
        root.setSpacing(12)
        self.setLayout(root)

        # Title
        title = QLabel("🏆 " + _("Warmup Complete!"))
        title.setAlignment(Qt.AlignCenter)
        title.setProperty("class", "main-title")
        title.setAccessibleName(_("Warmup Complete!"))
        root.addWidget(title)

        # Summary line
        ranked   = self.session.get_ranked_results()
        total    = len(ranked)
        correct  = self.session.correct_count()
        reason   = self.session.completion_reason()

        if reason == "wrong":
            summary_text = _("Warmup completed early wrong").format(correct=correct, total=total)
        elif reason == "skipped":
            summary_text = _("Warmup completed early skipped").format(correct=correct, total=total)
        else:
            summary_text = _("Warmup completed success").format(correct=correct, total=total)

        summary = QLabel(summary_text)
        summary.setAlignment(Qt.AlignCenter)
        summary.setWordWrap(True)
        summary.setProperty("class", "subtitle")
        summary.setAccessibleName(summary_text)
        root.addWidget(summary)

        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setFrameShadow(QFrame.Sunken)
        root.addWidget(divider)

        # Scrollable ranking list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        list_widget = QWidget()
        list_layout = QVBoxLayout(list_widget)
        list_layout.setSpacing(6)
        list_layout.setContentsMargins(0, 0, 0, 0)

        for rank, entry in enumerate(ranked, start=1):
            label_text = entry["label"]
            score      = entry["score"]
            emoji, tier_name = SCORE_INFO.get(score, ("?", "Unknown"))
            colour = SCORE_COLOURS.get(score, "#95A5A6")

            # Localize label dynamically
            parts = label_text.split("_")
            if len(parts) == 2:
                digit, operation = parts[0], parts[1].capitalize()
                translated_label_text = f"{digit} {_(operation)}"
            else:
                translated_label_text = _(label_text)

            row = QHBoxLayout()
            row.setSpacing(12)

            rank_lbl = QLabel(f"#{rank}")
            rank_lbl.setFixedWidth(36)
            rank_lbl.setFont(QFont("Arial", 13, QFont.Bold))
            rank_lbl.setAlignment(Qt.AlignCenter)
            row.addWidget(rank_lbl)

            type_lbl = QLabel(translated_label_text)
            type_lbl.setFont(QFont("Arial", 13))
            type_lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            row.addWidget(type_lbl)

            pts_lbl = QLabel(f"{emoji}  {_(tier_name)}  ({score:.1f} pt{'s' if score != 1.0 else ''})")
            pts_lbl.setFont(QFont("Arial", 13, QFont.Bold))
            pts_lbl.setAlignment(Qt.AlignRight)
            pts_lbl.setStyleSheet(f"color: {colour};")
            pts_lbl.setAccessibleName(f"{translated_label_text}: {_(tier_name)}, {score} points")
            row.addWidget(pts_lbl)

            row_widget = QWidget()
            row_widget.setLayout(row)
            row_widget.setStyleSheet(
                "QWidget { border-bottom: 1px solid rgba(128,128,128,0.2); padding: 4px 0; }"
            )
            list_layout.addWidget(row_widget)

        list_layout.addStretch()
        scroll.setWidget(list_widget)
        root.addWidget(scroll)

        root.addSpacing(8)

        # Continue button
        self.continue_btn = QPushButton("▶  " + _("Continue to Game Mode"))
        self.continue_btn.setMinimumSize(280, 70)
        self.continue_btn.setProperty("class", "menu-button")
        self.continue_btn.setAccessibleName(_("Continue to Game Mode"))
        self.continue_btn.setAccessibleDescription(
            _("Proceed to the Game Mode difficulty selector.")
        )
        self.continue_btn.clicked.connect(self._on_continue)
        root.addWidget(self.continue_btn, alignment=Qt.AlignCenter)

        QTimer.singleShot(300, self.continue_btn.setFocus)

    def _speak_results(self):
        if not (self.window and not self.window.is_muted and self.tts):
            return
        import random
        self.window.play_sound(f"finished-{random.randint(1, 3)}.mp3")
        ranked = self.session.get_ranked_results()
        if not ranked:
            return
        top = ranked[0]
        emoji, tier = SCORE_INFO.get(top["score"], ("", ""))
        
        # Translate top skill label
        # top_lbl = top['label']
        # parts = top_lbl.split("_")
        # if len(parts) == 2:
        #     digit, operation = parts[0], parts[1].capitalize()
        #     translated_top = f"{digit} {_(operation)}"
        # else:
        #     translated_top = _(top_lbl)

        # current_lang = getattr(lang_config, 'selected_language', 'English')
        # if current_lang == "മലയാളം":
        #     msg = f"വാംഅപ്പ് പൂർത്തിയായി! നിങ്ങളുടെ മികച്ച കഴിവിനുള്ള വിഭാഗം {translated_top} - {_(tier)} ആണ്. ഗെയിം മോഡ് ആരംഭിക്കാൻ തുടരുക അമർത്തുക."
        # elif current_lang == "हिंदी":
        #     msg = f"वार्मअप पूरा हुआ! आपका शीर्ष कौशल {translated_top} — {_(tier)} है। गेम मोड शुरू करने के लिए जारी रखें दबाएं।"
        # elif current_lang == "தமிழ்":
        #     msg = f"வார்ம்அப் முடிந்தது! உங்களின் சிறந்த திறன் {translated_top} — {_(tier)} ஆகும். கேம் பயன்முறையைத் தொடங்க தொடரவும் என்பதை அழுத்தவும்।"
        # elif current_lang == "عربي":
        #     msg = f"اكتمل الإحماء! مهاراتك الأفضل هي {translated_top} — {_(tier)}. اضغط على متابعة لبدء وضع اللعبة."
        # elif current_lang == "संस्कृत":
        #     msg = f"वार्मअप समाप्तम्! भवतः उत्तमं कौशलं {translated_top} — {_(tier)} अस्ति। गेम मोड आरब्धुं अनुवर्तस्व इति नुदतु।"
        # else:
        #     msg = (
        #         f"Warmup complete! Your top skill is {translated_top} — {_(tier)}. "
        #         f"Press Continue to start the Game Mode."
        #     )
        # QTimer.singleShot(600, lambda: self.tts.speak(msg))
        # focus_delay = 600 + len(msg) * 65 + 500
        # QTimer.singleShot(focus_delay, self.continue_btn.setFocus)
        self.continue_btn.setFocus()

    def _on_continue(self):
        if self.tts:
            self.tts.stop()
        self.on_continue()

    def cleanup(self):
        if self.tts:
            self.tts.stop()


# ---------------------------------------------------------------------------
# GameModeIntroWidget
# ---------------------------------------------------------------------------

class GameModeIntroWidget(QWidget):
    """Brief intro/resume screen shown before each Game Mode session."""

    def __init__(self, ranked, saved_state, on_start, window, tts):
        super().__init__()
        self.ranked = ranked or []; self.saved_state = saved_state
        self.on_start = on_start; self.window = window; self.tts = tts
        # self.setAccessibleName("Game Mode Introduction")
        self._init_ui()
        # self._speak_intro()

    def _init_ui(self):
        root = QVBoxLayout(); root.setAlignment(Qt.AlignCenter)
        root.setSpacing(16); root.setContentsMargins(50,30,50,30); self.setLayout(root)
        root.addStretch()
        title = QLabel("🎮 " + _("Game Mode")); title.setAlignment(Qt.AlignCenter)
        title.setProperty("class","main-title"); root.addWidget(title)
        if self.saved_state:
            lbl = self.saved_state.get("current_label", "Start")
            lbl_name = " ".join([p.capitalize() for p in lbl.split("_")])
            # Translate current label name
            parts = lbl.split("_")
            if len(parts) == 2:
                digit, operation = parts[0], parts[1].capitalize()
                translated_lbl_name = f"{digit} {_(operation)}"
            else:
                translated_lbl_name = _(lbl)
            status = QLabel("🔄  " + _("Resuming at {lbl_name}").format(lbl_name=translated_lbl_name))
            status.setStyleSheet("color:#27AE60;font-weight:bold;")
        else:
            status = QLabel(_("Starting fresh"))
        status.setAlignment(Qt.AlignCenter); status.setProperty("class","subtitle"); root.addWidget(status)

        
        rules_text = _(
            "How it works:\n"
            "• Reach correct threshold → promote to next skill\n"
            "• Too many wrong/skips → demote to easier skill\n"
            "• 90 seconds · correct answers add 3s · wrong cost 1s"
        )

        rules = QLabel(rules_text)
        rules.setWordWrap(True); rules.setProperty("class","subtitle"); rules.setMaximumWidth(500)
        root.addWidget(rules, alignment=Qt.AlignCenter); root.addSpacing(16)
        self.start_btn = QPushButton("🚀  " + _("Start Game"))
        self.start_btn.setMinimumSize(260,70); self.start_btn.setProperty("class","menu-button")
        self.start_btn.setAccessibleName(_("Start Game Mode")); self.start_btn.clicked.connect(self._on_start)
        root.addWidget(self.start_btn, alignment=Qt.AlignCenter); root.addStretch()
        QTimer.singleShot(200, self.start_btn.setFocus)

    def _speak_intro(self):
        if self.window and not self.window.is_muted and self.tts:
            current_lang = getattr(lang_config, 'selected_language', 'English')
            if current_lang == "മലയാളം":
                pfx = "ഗെയിം പുനരാരംഭിക്കുന്നു. " if self.saved_state else ""
                msg = pfx + "ഗെയിം മോഡ് തയ്യാറാണ്. ഗെയിം ആരംഭിക്കുക ക്ലിക്ക് ചെയ്യുക."
            elif current_lang == "हिंदी":
                pfx = "खेल फिर से शुरू हो रहा है। " if self.saved_state else ""
                msg = pfx + "गेम मोड तैयार है। गेम शुरू करें दबाएं।"
            elif current_lang == "தமிழ்":
                pfx = "விளையாட்டு மீண்டும் தொடங்குகிறது. " if self.saved_state else ""
                msg = pfx + "கேம் முறை தயாராக உள்ளது. விளையாட்டைத் தொடங்கவும் பொத்தானை அழுத்தவும்."
            elif current_lang == "عربي":
                pfx = "جاري استئناف اللعبة. " if self.saved_state else ""
                msg = pfx + "وضع اللعبة جاهز. اضغط على ابدأ اللعبة."
            elif current_lang == "संस्कृत":
                pfx = "खेलः पुनः आरभ्यते। " if self.saved_state else ""
                msg = pfx + "गेम मोड सज्जः अस्ति। ഗെയിം ആരംഭിക്കുക ക്ലിക്ക് ചെയ്യുക।"
            else:
                pfx = f"Resuming game. " if self.saved_state else ""
                msg = pfx + "Game Mode ready. Press Start Game."
            
            QTimer.singleShot(400, lambda: self.tts.speak(msg))

    def _on_start(self):
        if self.tts: self.tts.stop()
        self.on_start()

    def cleanup(self):
        if self.tts: self.tts.stop()


# ---------------------------------------------------------------------------
# GameModeWidget
# ---------------------------------------------------------------------------

class GameModeWidget(QWidget):
    """Active 90-second adaptive game session."""

    def __init__(self, session, window, tts, on_session_end):
        super().__init__()
        self.session = session; self.window = window; self.tts = tts
        self.on_session_end = on_session_end
        self._active = True; self._question_start_time = None
        self._current_answer = None; self._current_config = None
        # self.setAccessibleName("Game Mode Active"); 
        self._init_ui(); self._load_next_question()

    def showEvent(self, event):
        super().showEvent(event)
        # Force focus to the silent feedback label the exact moment the screen appears
        if hasattr(self, 'feedback_lbl'):
            self.feedback_lbl.setFocus()

    def _init_ui(self):
        root = QVBoxLayout(); root.setContentsMargins(20,8,20,8); root.setSpacing(6); self.setLayout(root)
        top = QHBoxLayout()
        self.level_lbl = QLabel(""); self.level_lbl.setProperty("class","subtitle")
        self.level_lbl.setFont(QFont("Arial",13,QFont.Bold)); top.addWidget(self.level_lbl, alignment=Qt.AlignLeft)
        self.phase_lbl = QLabel(""); self.phase_lbl.setProperty("class","subtitle")
        self.phase_lbl.setAlignment(Qt.AlignCenter); top.addWidget(self.phase_lbl)
        self.qcount_lbl = QLabel(""); self.qcount_lbl.setProperty("class","subtitle")
        self.qcount_lbl.setAlignment(Qt.AlignRight); top.addWidget(self.qcount_lbl, alignment=Qt.AlignRight)
        root.addLayout(top)
        self.timer_bar = QProgressBar()
        self.timer_bar.setMaximum(self.session.session_time); self.timer_bar.setMinimum(0)
        self.timer_bar.setValue(self.session.session_time); self.timer_bar.setTextVisible(True)
        self.timer_bar.setFormat("%vs"); self.timer_bar.setFixedHeight(18)
        self.timer_bar.setAccessibleName(""); self.timer_bar.setAccessibleDescription(""); root.addWidget(self.timer_bar)
        self.type_lbl = QLabel(""); self.type_lbl.setAlignment(Qt.AlignCenter)
        self.type_lbl.setProperty("class","main-title"); root.addWidget(self.type_lbl)
        root.addStretch(1)
        self.question_lbl = QLabel(""); self.question_lbl.setAlignment(Qt.AlignCenter)
        self.question_lbl.setWordWrap(True); self.question_lbl.setProperty("class","question-label")
        self.question_lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred); root.addWidget(self.question_lbl)
        root.addStretch(1)
        input_row = QHBoxLayout(); input_row.setSpacing(10); input_row.setAlignment(Qt.AlignCenter)
        self.input_box = QLineEdit(); self.input_box.setMinimumSize(220,55); self.input_box.setMaximumWidth(320)
        self.input_box.setAlignment(Qt.AlignCenter); self.input_box.setFont(QFont("Arial",16))
        self.input_box.setProperty("class","answer-input"); self.input_box.setAccessibleName(_("Answer input"))
        self.input_box.setValidator(QRegExpValidator(QRegExp(r"-?\d*\.?\d*")))
        self.input_box.returnPressed.connect(self._check_answer); input_row.addWidget(self.input_box)
        self.submit_btn = QPushButton("✓  " + _("Submit")); self.submit_btn.setMinimumSize(120,55)
        self.submit_btn.setProperty("class","menu-button"); self.submit_btn.setAccessibleName(_("Submit answer"))
        self.submit_btn.clicked.connect(self._check_answer); input_row.addWidget(self.submit_btn)
        root.addLayout(input_row); root.addSpacing(8)
        self.skip_btn = QPushButton("⏭  " + _("Skip")); self.skip_btn.setMinimumSize(160,44)
        self.skip_btn.setProperty("class","footer-button"); self.skip_btn.setFont(QFont("Arial",13))
        self.skip_btn.setAccessibleName(_("Skip this question")); self.skip_btn.clicked.connect(self._on_skip)
        root.addWidget(self.skip_btn, alignment=Qt.AlignCenter)
        self.feedback_lbl = QLabel(""); self.feedback_lbl.setAlignment(Qt.AlignCenter)
        self.feedback_lbl.setFont(QFont("Arial",20,QFont.Bold)); self.feedback_lbl.setFixedHeight(46)
        self.feedback_lbl.setFocusPolicy(Qt.StrongFocus)
        self.feedback_lbl.setAccessibleName(" ")
        self.feedback_lbl.setFocus()
        root.addWidget(self.feedback_lbl); root.addStretch(1)

    def _load_next_question(self):
        if not self._active: return
        self._current_config = self.session.get_next_question_config()
        if self._current_config is None: self._finish(); return
        processor = self.session.build_processor(self._current_config)
        if processor.df is None or processor.df.empty:
            self.session.skip_question(self._current_config); QTimer.singleShot(0, self._load_next_question); return
        question_text, self._current_answer = processor.get_questions()
        if question_text == "No questions found." or self._current_answer is None:
            self.session.skip_question(self._current_config); QTimer.singleShot(0, self._load_next_question); return
        
        # Localize level name dynamically
        lvl_name = self.session.level_name()
        parts = lvl_name.split(" ")
        if len(parts) == 2:
            digit, operation = parts[0], parts[1]
            translated_lvl_name = f"{digit} {_(operation)}"
        else:
            translated_lvl_name = _(lvl_name)
        
        self.level_lbl.setText(f"🎮 {translated_lvl_name}")
        self.phase_lbl.setText("")
        self.qcount_lbl.setText(_("Question") + f" {self.session.question_count+1}")
        
        # Localize question type label dynamically
        lbl_text = self._current_config["label"]
        parts = lbl_text.split("_")
        if len(parts) == 2:
            digit, operation = parts[0], parts[1].capitalize()
            translated_lbl = f"{digit} {_(operation)}"
        else:
            translated_lbl = _(lbl_text)
        self.type_lbl.setText(translated_lbl)

        ln = len(question_text)
        self.question_lbl.setStyleSheet("font-size:14pt;" if ln>120 else "font-size:18pt;" if ln>80 else "")
        self.question_lbl.setText(question_text)
        self.feedback_lbl.setText(""); self.input_box.clear()
        self.input_box.setEnabled(True); self.submit_btn.setEnabled(True); self.skip_btn.setEnabled(True)
        self._question_start_time = None
        audio_on = self.window and not self.window.is_muted
        if audio_on and self.tts:
            tts_text = f"{question_text}. {_('Type your answer')}"
            QTimer.singleShot(len(tts_text)*70+1500, self._on_tts_done); self.tts.speak(tts_text)
        else:
            self._on_tts_done()
        

    def _on_tts_done(self):
        if not self._active:
            return
        self._question_start_time = time()
        QTimer.singleShot(100, self.input_box.setFocus)

    def _check_answer(self):
        if not self._active: return
        user_text = self.input_box.text().strip()
        if not user_text: self.input_box.setFocus(); return
        try: is_correct = (float(user_text) == float(self._current_answer))
        except (TypeError, ValueError):
            self.feedback_lbl.setText(f'<span style="color:#E74C3C;">✗ {_("Invalid")}</span>'); self.input_box.setFocus(); return
        elapsed = (time()-self._question_start_time) if self._question_start_time else 0.0
        score   = self.session.submit_answer(self._current_config, is_correct, elapsed)
        self.input_box.setEnabled(False); self.submit_btn.setEnabled(False); self.skip_btn.setEnabled(False)
        if is_correct:
            self.window.time_remaining = min(self.window.time_remaining+3, self.session.session_time)
        else:
            self.window.time_remaining = max(0, self.window.time_remaining-1)
        self.update_timer(self.window.time_remaining)
        from question.warmup import save_game_session; save_game_session(self.session.save_state(self.window.time_remaining))
        
        current_lang = getattr(lang_config, 'selected_language', 'English')
        if is_correct:
            emoji, tier = SCORE_INFO.get(score, ("✓",""))
            self.feedback_lbl.setText(f'<span style="color:#27AE60;">{emoji} {_(tier)}</span>')
            if self.window and not self.window.is_muted:
                import random
                sound_index = random.randint(1, 3)
                if score == 1.0:
                    sound_file = f"excellent-{sound_index}.mp3"
                elif score == 0.5:
                    sound_file = f"good-{sound_index}.mp3"
                elif score == 0.2:
                    sound_file = f"not-bad-{sound_index}.mp3"
                else:
                    sound_file = f"okay-{sound_index}.mp3"
                self.window.play_sound(sound_file)

            # if self.tts and not self.window.is_muted:
            #     if current_lang == "മലയാളം":
            #         QTimer.singleShot(50, lambda t=tier: self.tts.speak(f"ശരിയാണ്! {_(t)}"))
            #     else:
            #         QTimer.singleShot(50, lambda t=tier: self.tts.speak(_(t)))
            QTimer.singleShot(1200, self._load_next_question)
        else:
            self.feedback_lbl.setText(f'<span style="color:#E74C3C;">✗ {_("Wrong")}</span>')
            if self.window and not self.window.is_muted:
                import random
                self.window.play_sound(f"wrong-anwser-{random.randint(1, 3)}.mp3")

            # if self.tts and not self.window.is_muted:
            #     if current_lang == "മലയാളം":
            #         QTimer.singleShot(50, lambda: self.tts.speak("തെറ്റാണ്."))
            #     else:
            #         QTimer.singleShot(50, lambda: self.tts.speak("Wrong"))
            QTimer.singleShot(900, self._load_next_question)

    def _on_skip(self):
        if not self._active: return
        self.session.skip_question(self._current_config)
        self.window.time_remaining = max(0, self.window.time_remaining-2)
        self.update_timer(self.window.time_remaining)
        from question.warmup import save_game_session; save_game_session(self.session.save_state(self.window.time_remaining))
        self.feedback_lbl.setText(f'<span style="color:#95A5A6;">⏭ {_("Skipped")}</span>')
        self.input_box.setEnabled(False); self.submit_btn.setEnabled(False); self.skip_btn.setEnabled(False)
        if self.window and not self.window.is_muted:
            self.window.play_sound("wrong-anwser-1.mp3")
        QTimer.singleShot(700, self._load_next_question)

    def update_timer(self, secs):
        self.timer_bar.setValue(secs)
        c = "#1D9E75" if secs>30 else "#EF9F27" if secs>15 else "#E24B4A"
        self.timer_bar.setStyleSheet(f"QProgressBar::chunk{{background-color:{c};border-radius:4px;}}")

    def _finish(self):
        self._active = False
        if self.tts: self.tts.stop()
        self.on_session_end()

    def cleanup(self):
        self._active = False
        if self.tts: self.tts.stop()


# ---------------------------------------------------------------------------
# GameModeReportWidget
# ---------------------------------------------------------------------------

class GameModeReportWidget(QWidget):
    """Post-session summary with updated ranking and Play Again button."""

    def __init__(self, session, window, tts, on_play_again):
        super().__init__()
        self.session = session; self.window = window; self.tts = tts; self.on_play_again = on_play_again
        self.setAccessibleName(_("Game Mode Results")); self._init_ui(); self._speak_summary()

    def _init_ui(self):
        root = QVBoxLayout(); root.setContentsMargins(40,16,40,16); root.setSpacing(10); self.setLayout(root)
        title = QLabel("🏆 " + _("Session Complete!")); title.setAlignment(Qt.AlignCenter)
        title.setProperty("class","main-title"); root.addWidget(title)
        acc = self.session.accuracy_pct(); lvl = self.session.level_name()
        
        # Localize final skill level dynamically
        parts = lvl.split(" ")
        if len(parts) == 2:
            digit, operation = parts[0], parts[1]
            translated_lvl = f"{digit} {_(operation)}"
        else:
            translated_lvl = _(lvl)
            
        stats_text = f"{_('Questions')}: {self.session.question_count}   ·   {_('Accuracy')}: {acc}%   ·   {_('Final Skill')}: {translated_lvl}"
        stats = QLabel(stats_text)
        stats.setAlignment(Qt.AlignCenter); stats.setProperty("class","subtitle"); root.addWidget(stats)
        div = QFrame(); div.setFrameShape(QFrame.HLine); root.addWidget(div)
        updated = self.session.get_ranked_results_updated()
        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        lw = QWidget(); ll = QVBoxLayout(lw); ll.setSpacing(4); ll.setContentsMargins(0,0,0,0)
        for rank, entry in enumerate(updated, 1):
            lbl = entry["label"]; score = entry["score"]; gained = entry.get("gained",0.0)
            key = 1.0 if score>=1.0 else 0.5 if score>=0.5 else 0.2 if score>0 else 0.0
            colour = SCORE_COLOURS.get(key,"#95A5A6"); gained_txt = f"+{gained:.1f}" if gained>0 else "–"
            
            # Localize label dynamically
            parts = lbl.split("_")
            if len(parts) == 2:
                digit, operation = parts[0], parts[1].capitalize()
                translated_lbl = f"{digit} {_(operation)}"
            else:
                translated_lbl = _(lbl)

            row = QHBoxLayout(); row.setSpacing(10)
            rl = QLabel(f"#{rank}"); rl.setFixedWidth(32); rl.setFont(QFont("Arial",12,QFont.Bold)); rl.setAlignment(Qt.AlignCenter)
            tl = QLabel(translated_lbl); tl.setFont(QFont("Arial",12)); tl.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Preferred)
            gl = QLabel(gained_txt); gl.setFont(QFont("Arial",12,QFont.Bold)); gl.setStyleSheet(f"color:{colour};"); gl.setFixedWidth(44); gl.setAlignment(Qt.AlignRight)
            sl = QLabel(f"{score:.1f}pt"); sl.setFont(QFont("Arial",12)); sl.setFixedWidth(48); sl.setAlignment(Qt.AlignRight)
            for w in (rl,tl,gl,sl): row.addWidget(w)
            rw = QWidget(); rw.setLayout(row); rw.setStyleSheet("QWidget{border-bottom:1px solid rgba(128,128,128,0.2);padding:3px 0;}"); ll.addWidget(rw)
        ll.addStretch(); scroll.setWidget(lw); root.addWidget(scroll)
        self.play_btn = QPushButton("🔄  " + _("Play Again")); self.play_btn.setMinimumSize(220,65)
        self.play_btn.setProperty("class","menu-button"); self.play_btn.setAccessibleName(_("Play Again"))
        self.play_btn.clicked.connect(self._on_play_again); root.addWidget(self.play_btn, alignment=Qt.AlignCenter)
        QTimer.singleShot(300, self.play_btn.setFocus)

    def _speak_summary(self):
        if not (self.window and not self.window.is_muted and self.tts): return
        import random
        self.window.play_sound(f"finished-{random.randint(1, 3)}.mp3")
        current_lang = getattr(lang_config, 'selected_language', 'English')
        pct = self.session.accuracy_pct()
        # if current_lang == "മലയാളം":
        #     msg = f"സെഷൻ പൂർത്തിയായി! {pct} ശതമാനം കൃത്യത. മികച്ച ശ്രമം!"
        # elif current_lang == "हिंदी":
        #     msg = f"सत्र पूरा हुआ! {pct} प्रतिशत सटीकता। शानदार प्रयास!"
        # elif current_lang == "தமிழ்":
        #     msg = f"அமர்வு முடிந்தது! {pct} சதவீத துல்லியம். சிறந்த முயற்சி!"
        # elif current_lang == "عربي":
        #     msg = f"اكتملت الجلسة! دقة بنسبة {pct} بالمائة. جهد رائع!"
        # elif current_lang == "संस्कृत":
        #     msg = f"സത്രം സമാപ്തം! {pct} ശതമാനം ശുദ്ധത. ഉത്തമൻ പ്രയാസം!"
        # else:
        #     msg = f"Session complete! {pct} percent accuracy. Great effort!"
        # QTimer.singleShot(600, lambda: self.tts.speak(msg))

    def _on_play_again(self):
        if self.tts: self.tts.stop()
        self.on_play_again()

    def cleanup(self):
        if self.tts: self.tts.stop()
