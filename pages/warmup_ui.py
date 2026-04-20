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
from language.language import tr


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
        self.setAccessibleName("Warmup Match Introduction")
        self._init_ui()
        self._speak_intro()

    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(18)
        layout.setContentsMargins(50, 30, 50, 30)
        self.setLayout(layout)

        layout.addStretch()

        title = QLabel("🏁 " + tr("Warmup Match"))
        title.setAlignment(Qt.AlignCenter)
        title.setProperty("class", "main-title")
        title.setAccessibleName("Warmup Match")
        layout.addWidget(title)

        layout.addSpacing(10)

        desc = QLabel(
            "Welcome! Before we begin the real game, let's do a quick "
            "Warmup Match so we can understand your strengths.\n\n"
            "You will answer one question from each of the different question types, "
            "starting from the easiest. Your speed and accuracy are measured "
            "after the question is read aloud.\n\n"
            "The warmup ends early only if you miss or skip too many questions."
        )
        desc.setAlignment(Qt.AlignCenter)
        desc.setWordWrap(True)
        desc.setProperty("class", "subtitle")
        desc.setMaximumWidth(560)
        layout.addWidget(desc, alignment=Qt.AlignCenter)

        layout.addSpacing(20)

        # Info row
        info_row = QHBoxLayout()
        info_row.setAlignment(Qt.AlignCenter)
        info_row.setSpacing(30)
        for icon, label_text in [("⏱️", "Speed matters"), ("🎯", "14 question types"), ("📊", "Ranked results")]:
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

        self.begin_btn = QPushButton("🚀  Begin Warmup")
        self.begin_btn.setMinimumSize(260, 70)
        self.begin_btn.setProperty("class", "menu-button")
        self.begin_btn.setAccessibleName("Begin Warmup")
        self.begin_btn.setAccessibleDescription(
            "Start the warmup match. You will answer 13 questions."
        )
        self.begin_btn.clicked.connect(self._on_begin)
        layout.addWidget(self.begin_btn, alignment=Qt.AlignCenter)

        layout.addStretch()

        QTimer.singleShot(200, self.begin_btn.setFocus)

    def _speak_intro(self):
        if self.window and not self.window.is_muted and self.tts:
            msg = (
                "Welcome to the Warmup Match! "
                "We will assess your strengths by asking one question from each type. "
                "Press Begin Warmup when you are ready."
            )
            QTimer.singleShot(400, lambda: self.tts.speak(msg))

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

        self.setAccessibleName("Warmup Question")
        self._init_ui()
        self._load_current_step()

    # ── UI setup ─────────────────────────────────────────────────────────────

    def _init_ui(self):
        root = QVBoxLayout()
        root.setContentsMargins(30, 10, 30, 10)
        root.setSpacing(8)
        self.setLayout(root)

        # Header row: title + step counter
        header = QHBoxLayout()
        warmup_lbl = QLabel("🏁 Warmup Match")
        warmup_lbl.setProperty("class", "subtitle")
        warmup_lbl.setAccessibleName("")
        header.addWidget(warmup_lbl, alignment=Qt.AlignLeft)

        self.step_counter_lbl = QLabel("")
        self.step_counter_lbl.setProperty("class", "subtitle")
        self.step_counter_lbl.setAlignment(Qt.AlignRight)
        header.addWidget(self.step_counter_lbl, alignment=Qt.AlignRight)
        root.addLayout(header)

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
        self.autoskip_bar.setFormat("Auto-skip in %vs")
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
        self.input_box.setPlaceholderText(tr("Enter your answer"))
        self.input_box.setFont(QFont("Arial", 16))
        self.input_box.setProperty("class", "answer-input")
        self.input_box.setAccessibleName(tr("Answer input"))
        validator = QRegExpValidator(QRegExp(r"-?\d*\.?\d*"))
        self.input_box.setValidator(validator)
        self.input_box.returnPressed.connect(self._check_answer)
        input_row.addWidget(self.input_box)

        self.submit_btn = QPushButton("✓  Submit")
        self.submit_btn.setMinimumSize(120, 55)
        self.submit_btn.setProperty("class", "menu-button")
        self.submit_btn.setAccessibleName("Submit answer")
        self.submit_btn.clicked.connect(self._check_answer)
        input_row.addWidget(self.submit_btn)

        root.addLayout(input_row)

        root.addSpacing(10)

        # Skip button (always visible, prominent)
        self.skip_btn = QPushButton("⏭  Skip this question")
        self.skip_btn.setMinimumSize(200, 48)
        self.skip_btn.setProperty("class", "footer-button")
        self.skip_btn.setFont(QFont("Arial", 13))
        self.skip_btn.setAccessibleName("Skip this question")
        self.skip_btn.setAccessibleDescription(
            "Skip the current question. Skipped questions score zero."
        )
        self.skip_btn.clicked.connect(self._on_skip)
        root.addWidget(self.skip_btn, alignment=Qt.AlignCenter)

        # Feedback label
        self.feedback_lbl = QLabel("")
        self.feedback_lbl.setAlignment(Qt.AlignCenter)
        self.feedback_lbl.setFont(QFont("Arial", 22, QFont.Bold))
        self.feedback_lbl.setFixedHeight(50)
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
        self.step_counter_lbl.setText(f"Question {step_num} / {total}")
        self.progress_bar.setValue(self.session.step_index)
        self.type_lbl.setText(step["label"])
        self.feedback_lbl.setText("")
        self.input_box.clear()
        self.input_box.setEnabled(True)
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
            tts_text = f"{question_text}. {tr('Type your answer')}"
            delay_ms = len(tts_text) * 70 + 1500
            self.tts.speak(tts_text)
            QTimer.singleShot(delay_ms, self._on_tts_done)
        else:
            self._on_tts_done()

        QTimer.singleShot(100, self.input_box.setFocus)

    def _on_tts_done(self):
        if not self._active:
            return
        self._question_start_time = time()
        self._autoskip_remaining  = AUTO_SKIP_SECONDS
        self.autoskip_bar.setValue(AUTO_SKIP_SECONDS)
        self.autoskip_bar.setVisible(True)
        self.autoskip_timer.start()
        self.autoskip_tick_timer.start()

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
            self.feedback_lbl.setText('<span style="color:#E74C3C;">✗ Invalid — try again</span>')
            self.input_box.setFocus()
            return

        elapsed = (time() - self._question_start_time) if self._question_start_time else 0.0
        score   = self.session.submit_answer(is_correct, elapsed)

        self.input_box.setEnabled(False)
        self.submit_btn.setEnabled(False)
        self.skip_btn.setEnabled(False)

        if is_correct:
            emoji, label = SCORE_INFO.get(score, ("✓", ""))
            self.feedback_lbl.setText(
                f'<span style="color:#27AE60; font-size:22pt;">{emoji} Correct!  {label}</span>'
            )
            if self.tts and self.window and not self.window.is_muted:
                QTimer.singleShot(50, lambda: self.tts.speak(f"Correct! {label}"))
            QTimer.singleShot(1400, self._advance)
        else:
            self.feedback_lbl.setText(
                f'<span style="color:#E74C3C; font-size:22pt;">✗ Wrong — moving on</span>'
            )
            if self.tts and self.window and not self.window.is_muted:
                QTimer.singleShot(50, lambda: self.tts.speak("Wrong."))
            QTimer.singleShot(1200, self._advance)

    def _on_skip(self):
        if not self._active:
            return
        self._stop_timers()
        self.session.skip_question()
        self.input_box.setEnabled(False)
        self.submit_btn.setEnabled(False)
        self.skip_btn.setEnabled(False)
        self.feedback_lbl.setText('<span style="color:#95A5A6; font-size:18pt;">⏭ Skipped</span>')
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
        self.feedback_lbl.setText('<span style="color:#95A5A6; font-size:18pt;">⏱ Time out — auto-skipped</span>')
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
        self.on_complete()

    # ── Utilities ────────────────────────────────────────────────────────────

    def _stop_timers(self):
        self.autoskip_timer.stop()
        self.autoskip_tick_timer.stop()
        self.autoskip_bar.setVisible(False)

    def cleanup(self):
        self._active = False
        self._stop_timers()
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
        self.setAccessibleName("Warmup Results")
        self._init_ui()
        self._speak_results()

    def _init_ui(self):
        root = QVBoxLayout()
        root.setContentsMargins(40, 20, 40, 20)
        root.setSpacing(12)
        self.setLayout(root)

        # Title
        title = QLabel("🏆 Warmup Complete!")
        title.setAlignment(Qt.AlignCenter)
        title.setProperty("class", "main-title")
        title.setAccessibleName("Warmup Complete")
        root.addWidget(title)

        # Summary line
        ranked   = self.session.get_ranked_results()
        total    = len(ranked)
        correct  = self.session.correct_count()
        reason   = self.session.completion_reason()

        if reason == "wrong":
            summary_text = f"You answered {correct}/{total} questions correctly. The warmup ended early — that's okay!"
        elif reason == "skipped":
            summary_text = f"You answered {correct}/{total} questions. The warmup ended after too many skips — no worries!"
        else:
            summary_text = f"Great job completing all {total} questions! You got {correct} correct."

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

            row = QHBoxLayout()
            row.setSpacing(12)

            rank_lbl = QLabel(f"#{rank}")
            rank_lbl.setFixedWidth(36)
            rank_lbl.setFont(QFont("Arial", 13, QFont.Bold))
            rank_lbl.setAlignment(Qt.AlignCenter)
            row.addWidget(rank_lbl)

            type_lbl = QLabel(label_text)
            type_lbl.setFont(QFont("Arial", 13))
            type_lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            row.addWidget(type_lbl)

            pts_lbl = QLabel(f"{emoji}  {tier_name}  ({score:.1f} pt{'s' if score != 1.0 else ''})")
            pts_lbl.setFont(QFont("Arial", 13, QFont.Bold))
            pts_lbl.setAlignment(Qt.AlignRight)
            pts_lbl.setStyleSheet(f"color: {colour};")
            pts_lbl.setAccessibleName(f"{label_text}: {tier_name}, {score} points")
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
        self.continue_btn = QPushButton("▶  Continue to Game Mode")
        self.continue_btn.setMinimumSize(280, 70)
        self.continue_btn.setProperty("class", "menu-button")
        self.continue_btn.setAccessibleName("Continue to Game Mode")
        self.continue_btn.setAccessibleDescription(
            "Proceed to the Game Mode difficulty selector."
        )
        self.continue_btn.clicked.connect(self._on_continue)
        root.addWidget(self.continue_btn, alignment=Qt.AlignCenter)

        QTimer.singleShot(300, self.continue_btn.setFocus)

    def _speak_results(self):
        if not (self.window and not self.window.is_muted and self.tts):
            return
        ranked = self.session.get_ranked_results()
        if not ranked:
            return
        top = ranked[0]
        emoji, tier = SCORE_INFO.get(top["score"], ("", ""))
        msg = (
            f"Warmup complete! Your top skill is {top['label']} — {tier}. "
            f"Press Continue to start the Game Mode."
        )
        QTimer.singleShot(600, lambda: self.tts.speak(msg))
        focus_delay = 600 + len(msg) * 65 + 500
        QTimer.singleShot(focus_delay, self.continue_btn.setFocus)

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
        self.setAccessibleName("Game Mode Introduction")
        self._init_ui(); self._speak_intro()

    def _init_ui(self):
        root = QVBoxLayout(); root.setAlignment(Qt.AlignCenter)
        root.setSpacing(16); root.setContentsMargins(50,30,50,30); self.setLayout(root)
        root.addStretch()
        title = QLabel("🎮 Game Mode"); title.setAlignment(Qt.AlignCenter)
        title.setProperty("class","main-title"); root.addWidget(title)
        if self.saved_state:
            lbl = self.saved_state.get("current_label", "Start")
            lbl_name = " ".join([p.capitalize() for p in lbl.split("_")])
            status = QLabel(f"🔄  Resuming at {lbl_name}")
            status.setStyleSheet("color:#27AE60;font-weight:bold;")
        else:
            status = QLabel("Starting fresh")
        status.setAlignment(Qt.AlignCenter); status.setProperty("class","subtitle"); root.addWidget(status)
        rules = QLabel("How it works:\n• Reach correct threshold → promote to next skill\n"
                       "• Too many wrong/skips → demote to easier skill\n"
                       "• 90 seconds · correct answers add 3s · wrong cost 1s")
        rules.setWordWrap(True); rules.setProperty("class","subtitle"); rules.setMaximumWidth(500)
        root.addWidget(rules, alignment=Qt.AlignCenter); root.addSpacing(16)
        self.start_btn = QPushButton("🚀  Start Game")
        self.start_btn.setMinimumSize(260,70); self.start_btn.setProperty("class","menu-button")
        self.start_btn.setAccessibleName("Start Game Mode"); self.start_btn.clicked.connect(self._on_start)
        root.addWidget(self.start_btn, alignment=Qt.AlignCenter); root.addStretch()
        QTimer.singleShot(200, self.start_btn.setFocus)

    def _speak_intro(self):
        if self.window and not self.window.is_muted and self.tts:
            pfx = f"Resuming game. " if self.saved_state else ""
            QTimer.singleShot(400, lambda: self.tts.speak(pfx + "Game Mode ready. Press Start Game."))

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
        self.setAccessibleName("Game Mode Active"); self._init_ui(); self._load_next_question()

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
        self.input_box.setProperty("class","answer-input"); self.input_box.setAccessibleName(tr("Answer input"))
        self.input_box.setValidator(QRegExpValidator(QRegExp(r"-?\d*\.?\d*")))
        self.input_box.returnPressed.connect(self._check_answer); input_row.addWidget(self.input_box)
        self.submit_btn = QPushButton("✓  Submit"); self.submit_btn.setMinimumSize(120,55)
        self.submit_btn.setProperty("class","menu-button"); self.submit_btn.setAccessibleName("Submit answer")
        self.submit_btn.clicked.connect(self._check_answer); input_row.addWidget(self.submit_btn)
        root.addLayout(input_row); root.addSpacing(8)
        self.skip_btn = QPushButton("⏭  Skip"); self.skip_btn.setMinimumSize(160,44)
        self.skip_btn.setProperty("class","footer-button"); self.skip_btn.setFont(QFont("Arial",13))
        self.skip_btn.setAccessibleName("Skip this question"); self.skip_btn.clicked.connect(self._on_skip)
        root.addWidget(self.skip_btn, alignment=Qt.AlignCenter)
        self.feedback_lbl = QLabel(""); self.feedback_lbl.setAlignment(Qt.AlignCenter)
        self.feedback_lbl.setFont(QFont("Arial",20,QFont.Bold)); self.feedback_lbl.setFixedHeight(46)
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
        self.level_lbl.setText(f"🎮 {self.session.level_name()}")
        self.phase_lbl.setText("")
        self.qcount_lbl.setText(f"Q{self.session.question_count+1}")
        self.type_lbl.setText(self._current_config["label"])
        ln = len(question_text)
        self.question_lbl.setStyleSheet("font-size:14pt;" if ln>120 else "font-size:18pt;" if ln>80 else "")
        self.question_lbl.setText(question_text)
        self.feedback_lbl.setText(""); self.input_box.clear()
        self.input_box.setEnabled(True); self.submit_btn.setEnabled(True); self.skip_btn.setEnabled(True)
        self._question_start_time = None
        audio_on = self.window and not self.window.is_muted
        if audio_on and self.tts:
            tts_text = f"{question_text}. {tr('Type your answer')}"
            QTimer.singleShot(len(tts_text)*70+1500, self._on_tts_done); self.tts.speak(tts_text)
        else:
            self._on_tts_done()
        QTimer.singleShot(100, self.input_box.setFocus)

    def _on_tts_done(self):
        if self._active: self._question_start_time = time()

    def _check_answer(self):
        if not self._active: return
        user_text = self.input_box.text().strip()
        if not user_text: self.input_box.setFocus(); return
        try: is_correct = (float(user_text) == float(self._current_answer))
        except (TypeError, ValueError):
            self.feedback_lbl.setText('<span style="color:#E74C3C;">✗ Invalid</span>'); self.input_box.setFocus(); return
        elapsed = (time()-self._question_start_time) if self._question_start_time else 0.0
        score   = self.session.submit_answer(self._current_config, is_correct, elapsed)
        self.input_box.setEnabled(False); self.submit_btn.setEnabled(False); self.skip_btn.setEnabled(False)
        if is_correct:
            self.window.time_remaining = min(self.window.time_remaining+3, self.session.session_time)
        else:
            self.window.time_remaining = max(0, self.window.time_remaining-1)
        self.update_timer(self.window.time_remaining)
        from question.warmup import save_game_session; save_game_session(self.session.save_state())
        if is_correct:
            emoji, tier = SCORE_INFO.get(score, ("✓",""))
            self.feedback_lbl.setText(f'<span style="color:#27AE60;">{emoji} {tier}</span>')
            if self.tts and not self.window.is_muted: QTimer.singleShot(50, lambda t=tier: self.tts.speak(t))
            QTimer.singleShot(1200, self._load_next_question)
        else:
            self.feedback_lbl.setText('<span style="color:#E74C3C;">✗ Wrong</span>')
            if self.tts and not self.window.is_muted: QTimer.singleShot(50, lambda: self.tts.speak("Wrong"))
            QTimer.singleShot(900, self._load_next_question)

    def _on_skip(self):
        if not self._active: return
        self.session.skip_question(self._current_config)
        self.window.time_remaining = max(0, self.window.time_remaining-2)
        self.update_timer(self.window.time_remaining)
        from question.warmup import save_game_session; save_game_session(self.session.save_state())
        self.feedback_lbl.setText('<span style="color:#95A5A6;">⏭ Skipped</span>')
        self.input_box.setEnabled(False); self.submit_btn.setEnabled(False); self.skip_btn.setEnabled(False)
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
        self.setAccessibleName("Game Mode Results"); self._init_ui(); self._speak_summary()

    def _init_ui(self):
        root = QVBoxLayout(); root.setContentsMargins(40,16,40,16); root.setSpacing(10); self.setLayout(root)
        title = QLabel("🏆 Session Complete!"); title.setAlignment(Qt.AlignCenter)
        title.setProperty("class","main-title"); root.addWidget(title)
        acc = self.session.accuracy_pct(); lvl = self.session.level_name()
        stats = QLabel(f"Questions: {self.session.question_count}   ·   Accuracy: {acc}%   ·   Final Skill: {lvl}")
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
            row = QHBoxLayout(); row.setSpacing(10)
            rl = QLabel(f"#{rank}"); rl.setFixedWidth(32); rl.setFont(QFont("Arial",12,QFont.Bold)); rl.setAlignment(Qt.AlignCenter)
            tl = QLabel(lbl); tl.setFont(QFont("Arial",12)); tl.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Preferred)
            gl = QLabel(gained_txt); gl.setFont(QFont("Arial",12,QFont.Bold)); gl.setStyleSheet(f"color:{colour};"); gl.setFixedWidth(44); gl.setAlignment(Qt.AlignRight)
            sl = QLabel(f"{score:.1f}pt"); sl.setFont(QFont("Arial",12)); sl.setFixedWidth(48); sl.setAlignment(Qt.AlignRight)
            for w in (rl,tl,gl,sl): row.addWidget(w)
            rw = QWidget(); rw.setLayout(row); rw.setStyleSheet("QWidget{border-bottom:1px solid rgba(128,128,128,0.2);padding:3px 0;}"); ll.addWidget(rw)
        ll.addStretch(); scroll.setWidget(lw); root.addWidget(scroll)
        self.play_btn = QPushButton("🔄  Play Again"); self.play_btn.setMinimumSize(220,65)
        self.play_btn.setProperty("class","menu-button"); self.play_btn.setAccessibleName("Play Again")
        self.play_btn.clicked.connect(self._on_play_again); root.addWidget(self.play_btn, alignment=Qt.AlignCenter)
        QTimer.singleShot(300, self.play_btn.setFocus)

    def _speak_summary(self):
        if not (self.window and not self.window.is_muted and self.tts): return
        msg = f"Session complete! {self.session.accuracy_pct()} percent accuracy. Great effort!"
        QTimer.singleShot(600, lambda: self.tts.speak(msg))

    def _on_play_again(self):
        if self.tts: self.tts.stop()
        self.on_play_again()

    def cleanup(self):
        if self.tts: self.tts.stop()
