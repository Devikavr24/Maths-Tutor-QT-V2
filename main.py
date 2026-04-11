import sys, os, subprocess
from PyQt5 import sip

# ── Accessibility: Enable the Qt5 ↔ AT-SPI bridge for Linux screen readers ──
os.environ["QT_LINUX_ACCESSIBILITY_ALWAYS_ON"] = "1"
os.environ["QT_ACCESSIBILITY"] = "1"

if sys.platform.startswith("linux"):
    os.environ.setdefault("QT_QPA_PLATFORM", "xcb")
    try:
        subprocess.run(
            ["gsettings", "set", "org.gnome.desktop.interface",
             "toolkit-accessibility", "true"],
            check=False, timeout=3, capture_output=True,
        )
    except FileNotFoundError:
        pass  

    _sys_plugins_dir = "/usr/lib/x86_64-linux-gnu/qt5/plugins"
    if os.path.isdir(_sys_plugins_dir):
        os.environ.setdefault("QT_PLUGIN_PATH", _sys_plugins_dir)
        os.environ.setdefault("QT_QPA_PLATFORM_PLUGIN_PATH", os.path.join(_sys_plugins_dir, "platforms"))

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QDialog, QVBoxLayout,
    QPushButton, QComboBox, QHBoxLayout, QCheckBox, QFrame,
    QWidget, QGridLayout, QStackedWidget, QSizePolicy, QShortcut, QMessageBox,
    QBoxLayout
)
from PyQt5.QtCore import Qt, QUrl, QSize, QTimer
from question.loader import QuestionProcessor
from pages.shared_ui import create_footer_buttons, apply_theme, SettingsDialog, create_main_footer_buttons, QuestionWidget, setup_exit_handling
from pages.ques_functions import load_pages, upload_excel
from tts.tts_worker import TextToSpeech

from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

from language.language import get_saved_language, save_selected_language_to_file, tr, set_language

from PyQt5.QtGui import QMovie, QKeySequence, QPixmap, QFont, QIcon
from PyQt5.QtCore import Qt

def clear_layout(layout):
    if layout is None:
        return
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget:
            widget.setParent(None)
            widget.deleteLater()


class RootWindow(QDialog):
    def __init__(self, minimal=False):
        super().__init__()
        self.minimal = minimal
        self.remember = False
        self.setWindowTitle("Maths Tutor - Language Selection Window")
        self.setFixedSize(400, 250 if not self.minimal else 150)
        self.init_ui()
        self.load_style("language_dialog.qss")
        self.closeEvent = lambda event: event.accept()

    def init_ui(self):
        layout = QVBoxLayout()

        if not self.minimal:
            title_label = QLabel("Welcome to Maths Tutor!")
            title_label.setProperty("class", "title")
            title_label.setAccessibleName("Welcome to Maths Tutor")
            layout.addWidget(title_label)
            layout.addSpacing(15)

        language_label = QLabel("Select your preferred language:")
        language_label.setProperty("class", "subtitle")

        languages = ["English", "हिंदी", "മലയാളം", "தமிழ்", "عربي", "संस्कृत"]
        self.language_combo = QComboBox()
        self.language_combo.addItems(languages)
        self.language_combo.setProperty("class", "combo-box")

        language_label.setBuddy(self.language_combo)
        self.language_combo.setAccessibleName("Language Selection")
        self.language_combo.setAccessibleDescription("Choose from English, Hindi, Malayalam, Tamil, Arabic, or Sanskrit")

        layout.addWidget(language_label)
        layout.addWidget(self.language_combo)

        if not self.minimal:
            self.remember_check = QCheckBox("Remember my selection")
            self.remember_check.setChecked(False)
            self.remember_check.setProperty("class", "checkbox")
            self.remember_check.setStyleSheet("color: #ffffff;")
            self.remember_check.setAccessibleName("Remember my selection")
            self.remember_check.setAccessibleDescription("If checked, the app will skip this dialog next time")
            layout.addWidget(self.remember_check)

        layout.addStretch()

        if not self.minimal:
            layout.addWidget(self.create_line())
        self.ok_button = QPushButton("Continue")
        self.ok_button.setDefault(True)
        self.ok_button.setAutoDefault(True)
        QTimer.singleShot(100, lambda: self.language_combo.setFocus())
        self.ok_button.setAccessibleName("Continue")
        self.ok_button.setAccessibleDescription("Confirm language selection and continue to the app")

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setAutoDefault(False)
        self.cancel_button.setShortcut(Qt.Key_Escape)
        self.cancel_button.setProperty("class", "danger-button")
        self.cancel_button.setAccessibleName("Cancel")
        self.cancel_button.setAccessibleDescription("Close the dialog without selecting a language")

        btns = QHBoxLayout()
        btns.addStretch()
        btns.addWidget(self.cancel_button)
        btns.addWidget(self.ok_button)
        layout.addLayout(btns)

        self.setLayout(layout)
        self.cancel_button.clicked.connect(self.reject)
        self.ok_button.clicked.connect(self.handle_continue)

        QWidget.setTabOrder(self.language_combo, self.ok_button)
        if not self.minimal:
            QWidget.setTabOrder(self.language_combo, self.remember_check)
            QWidget.setTabOrder(self.remember_check, self.ok_button)
        QWidget.setTabOrder(self.ok_button, self.cancel_button)

    def handle_continue(self):
        selected = self.language_combo.currentText()
        set_language(selected)
        print("Language selected:", selected)
        self.remember = (hasattr(self, 'remember_check') and self.remember_check.isChecked()) if not self.minimal else False

        if self.remember:
            print("self.remember working")
            save_selected_language_to_file(selected)
        self.accept()

    def create_line(self):
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        return line

    def load_style(self, qss_file):
        style_path = os.path.join("styles", qss_file)
        if os.path.exists(style_path):
            with open(style_path, "r") as f:
                self.setStyleSheet(f.read())


class MainWindow(QMainWindow):
    def __init__(self, language="English"):
        super().__init__()

        self.language = language
        set_language(self.language)

        self.setWindowTitle(f"Maths Tutor - {self.language}")
        self.resize(900, 600)
        self.setMinimumSize(800, 550)
        self.current_difficulty = 1
        self.section_pages = {}
        self.is_muted = False

        setup_exit_handling(self, require_confirmation=True)
        self.init_ui()

        self.tts = TextToSpeech()
        self.tts.play_custom_sound_signal.connect(self.play_sound)
        self.base_qss = ""
        self.load_style("main_window.qss")
        self.current_theme = "light"

        self.media_player = QMediaPlayer()
        self.bg_player = QMediaPlayer()
        self.bg_player.setVolume(30)
        self.is_muted = False
        self.play_background_music()

        self.difficulty_index = 1

        self.game_timer = QTimer(self)
        self.game_timer.setInterval(1000)
        self.game_timer.timeout.connect(self._on_game_tick)

        self._slower_shortcut = QShortcut(QKeySequence("Ctrl+;"), self)
        self._slower_shortcut.activated.connect(self._on_slower)

        self._faster_shortcut = QShortcut(QKeySequence("Alt+;"), self)
        self._faster_shortcut.activated.connect(self._on_faster)

        self._repeat_shortcut = QShortcut(QKeySequence("Ctrl+R"), self)
        self._repeat_shortcut.activated.connect(self._on_repeat_question)

    def refresh_ui(self, new_language):
        print(f"[System] Refreshing UI to {new_language}...")
        self.language = new_language
        set_language(new_language)
        self.setWindowTitle(f"Maths Tutor - {self.language}")

        if hasattr(self, 'tts'):
            self.tts.stop()

        self.section_pages = {}
        if hasattr(self, 'game_mode_container'):
            del self.game_mode_container
        if hasattr(self, '_quickplay_question_widget'):
            del self._quickplay_question_widget
        if hasattr(self, 'quickplay_container'):
            del self.quickplay_container

        for attr in ('_warmup_intro_widget', '_warmup_question_widget', '_warmup_ranking_widget'):
            widget = getattr(self, attr, None)
            if widget:
                try: widget.cleanup()
                except Exception: pass
                delattr(self, attr)
        if hasattr(self, '_warmup_session'): del self._warmup_session

        for attr in ('_gamemode_intro', 'game_mode_widget'):
            widget = getattr(self, attr, None)
            if widget:
                try: widget.cleanup()
                except Exception: pass
                delattr(self, attr)
        if hasattr(self, '_game_session_new'): del self._game_session_new

        self.init_ui()
        apply_theme(self.central_widget, self.current_theme)

    def resizeEvent(self, event):
        super(MainWindow, self).resizeEvent(event)
        self.update_dynamic_styles()

    def init_ui(self):
        self.central_widget = QWidget()
        self.central_widget.setProperty("class", "central-widget")
        self.central_widget.setProperty("theme", "light")
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(25, 15, 25, 15)
        self.central_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.central_widget)

        self.current_theme = "light"

        self.theme_button = QPushButton("🌙")
        self.theme_button.setToolTip("Toggle Light/Dark Theme")
        self.theme_button.clicked.connect(self.toggle_theme)
        self.theme_button.setAccessibleName("Toggle theme. Currently light mode")
        self.theme_button.setAccessibleDescription("")
        self.theme_button.setProperty("class", "menu-button")
        self.theme_button.setFocusPolicy(Qt.TabFocus)

        self.top_bar = QWidget()
        self.top_bar_layout = QHBoxLayout(self.top_bar)
        self.top_bar_layout.setContentsMargins(0, 0, 0, 0)
        self.top_bar_layout.setSpacing(10)
        self.top_bar_layout.addWidget(self.theme_button, alignment=Qt.AlignLeft)
        self.top_bar_layout.addStretch()

        self.main_layout.addWidget(self.top_bar)

        self.menu_widget = QWidget()
        menu_layout = QVBoxLayout()
        menu_layout.setSpacing(20)
        self.menu_widget.setLayout(menu_layout)

        menu_layout.addStretch()

        title = QLabel(tr("🎓 Learning Mode"))
        title.setAlignment(Qt.AlignCenter)
        title.setProperty("class", "main-title")
        menu_layout.addWidget(title, alignment=Qt.AlignCenter)

        self.learn_mode_layout = QHBoxLayout()
        self.learn_mode_layout.setSpacing(40)
        self.learn_mode_layout.setAlignment(Qt.AlignCenter)

        self.gif_label_learn = QLabel()
        self.gif_label_learn.setAlignment(Qt.AlignCenter)
        self.gif_label_learn.setAccessibleName("")
        self.gif_label_learn.setAccessibleDescription("")
        self.movie_learn = QMovie("images/welcome-2.gif")
        self.movie_learn.setScaledSize(QSize(240, 240))
        self.gif_label_learn.setMovie(self.movie_learn)
        self.movie_learn.start()

        self.gif_learn_container = QWidget()
        gif_layout = QHBoxLayout(self.gif_learn_container)
        gif_layout.setContentsMargins(0, 0, 0, 0)
        gif_layout.addWidget(self.gif_label_learn, alignment=Qt.AlignCenter)

        self.buttons_learn_widget = QWidget()
        self.buttons_learn_widget.setLayout(self.create_buttons())

        self.learn_mode_layout.addWidget(self.gif_learn_container, alignment=Qt.AlignCenter)
        self.learn_mode_layout.addWidget(self.buttons_learn_widget, alignment=Qt.AlignCenter)

        menu_layout.addLayout(self.learn_mode_layout)
        menu_layout.addStretch()

        self.stack = QStackedWidget()
        self.stack.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.stack.setAccessibleName("Content area")

        self.startup_widget = self.create_mode_selection_page()
        self.stack.addWidget(self.startup_widget)

        self.stack.addWidget(self.menu_widget)

        self.stack.setCurrentWidget(self.startup_widget)

        self.main_layout.addWidget(self.stack)

        self.central_widget.setStyleSheet("""
            QWidget { background-repeat: no-repeat; }
            QStackedWidget > QWidget { background: transparent; }
        """)

        self.main_footer = create_main_footer_buttons(self)
        self.section_footer = self.create_section_footer()

        for footer in (self.main_footer, self.section_footer):
            footer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            footer.setMinimumHeight(63)

        self.main_layout.addWidget(self.main_footer)
        self.main_layout.addWidget(self.section_footer)

        self.section_footer.hide()

        back_btn = self.main_footer.findChild(QPushButton, tr("Back to Menu").lower().replace(" ", "_"))
        if back_btn:
            back_btn.hide()

        apply_theme(self.central_widget, self.current_theme)

        self.focus_story_button()
        self.focus_quickplay_button()

    def _get_question_text(self):
        current_page = self.stack.currentWidget()
        if current_page:
            question_widget = current_page.findChild(QuestionWidget)
            if question_widget and hasattr(question_widget, 'label'):
                text = question_widget.label.text()
                if text:
                    return text
        return None

    def _on_repeat_question(self):
        question_text = self._get_question_text()
        if question_text:
            if hasattr(self, 'tts'):
                self.tts.speak(question_text)
                print(f"[Ctrl+R] Repeating question: {question_text}")
            qw = self.stack.currentWidget().findChild(QuestionWidget) if self.stack.currentWidget() else None
            if qw:
                qw.increment_replay()

    def _on_slower(self):
        step = self.tts.RATE_STEP
        current_rate = self.tts.speech_rate
        new_rate = max(50, current_rate - step)
        if self.tts.is_speaking:
            if new_rate != current_rate:
                self.tts.set_rate(new_rate)
                print(f"[Ctrl+;] Speed decreased: {new_rate} WPM")
        else:
            if new_rate != current_rate:
                self.tts.set_rate(new_rate)
            question_text = self._get_question_text()
            if question_text:
                self.tts.speak(question_text)
                print(f"[Ctrl+;] Re-reading at {self.tts.speech_rate} WPM: {question_text}")
                qw = self.stack.currentWidget().findChild(QuestionWidget) if self.stack.currentWidget() else None
                if qw:
                    qw.increment_replay()

    def _on_faster(self):
        step = self.tts.RATE_STEP
        default = self.tts.DEFAULT_RATE
        current_rate = self.tts.speech_rate
        if self.tts.is_speaking:
            new_rate = min(300, current_rate + step)
            if new_rate != current_rate:
                self.tts.set_rate(new_rate)
                print(f"[Alt+;] Speed increased: {new_rate} WPM")
        else:
            max_idle_rate = default + step
            new_rate = min(max_idle_rate, current_rate + step)
            if new_rate != current_rate:
                self.tts.set_rate(new_rate)
            question_text = self._get_question_text()
            if question_text:
                self.tts.speak(question_text)
                print(f"[Alt+;] Re-reading at {self.tts.speech_rate} WPM: {question_text}")
                qw = self.stack.currentWidget().findChild(QuestionWidget) if self.stack.currentWidget() else None
                if qw:
                    qw.increment_replay()

    def focus_story_button(self):
        for btn in self.menu_buttons:
            if btn.text() == tr("Story"):
                btn.setFocus()
                break

    def focus_quickplay_button(self):
        if hasattr(self, "quickPlayButton") and self.quickPlayButton and not sip.isdeleted(self.quickPlayButton):
            self.quickPlayButton.setFocus()

    def create_mode_selection_page(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        widget.setLayout(layout)

        title = QLabel(tr("welcome"))
        title.setAlignment(Qt.AlignCenter)
        title.setProperty("class", "main-title")
        layout.addWidget(title, alignment=Qt.AlignCenter)

        subtitle = QLabel(tr("ready").format(lang=self.language))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setProperty("class", "subtitle")
        layout.addWidget(subtitle, alignment=Qt.AlignCenter)
        layout.addSpacing(30)

        content_layout = QHBoxLayout()
        content_layout.setSpacing(60)
        content_layout.setAlignment(Qt.AlignCenter)

        gif_label = QLabel()
        gif_label.setAlignment(Qt.AlignCenter)
        movie = QMovie("images/welcome-1.gif")
        movie.setScaledSize(QSize(280, 280))
        gif_label.setMovie(movie)
        movie.start()
        self._welcome_movie = movie
        content_layout.addWidget(gif_label, alignment=Qt.AlignCenter)

        buttons_widget = QWidget()
        buttons_layout = QVBoxLayout(buttons_widget)
        buttons_layout.setSpacing(15)
        buttons_layout.setAlignment(Qt.AlignCenter)

        buttons = [
            (tr("⚡Quickplay"), self.start_quickplay_mode),
            (tr("🎮 Game Mode"), self.start_game_mode),
            (tr("🎓 Learning Mode"), self.start_learning_mode)
        ]
        for text, callback in buttons:
            btn = QPushButton(text)
            btn.setMinimumHeight(65)
            btn.setMaximumHeight(80)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.setProperty("class", "menu-button")
            btn.setProperty("theme", self.current_theme)
            btn.clicked.connect(callback)

            clean_text = text.replace("⚡", "").replace("🎮", "").replace("🎓", "").strip()
            btn.setAccessibleName(clean_text)
            btn.setAccessibleDescription(f"Start {clean_text}")
            buttons_layout.addWidget(btn)

            if "Quickplay" in text or "त्वरित" in text or "Quickplay" in clean_text:
                self.quickPlayButton = btn

        content_layout.addWidget(buttons_widget, alignment=Qt.AlignCenter)
        layout.addLayout(content_layout)

        return widget

    def _switch_to_page(self, widget_to_show):
        if widget_to_show not in (self.startup_widget, self.menu_widget):
            self.stack.addWidget(widget_to_show)
        self.stack.setCurrentWidget(widget_to_show)

        for i in reversed(range(self.stack.count())):
            w = self.stack.widget(i)
            if w not in (self.startup_widget, self.menu_widget, widget_to_show):
                self.stack.removeWidget(w)
        print(f"[DEBUG] QStackedWidget count: {self.stack.count()}")

    def start_learning_mode(self):
        self._switch_to_page(self.menu_widget)
        self.main_footer.show()
        self.section_footer.hide()
        back_btn = self.main_footer.findChild(QPushButton, tr("Back to Menu").lower().replace(" ", "_"))
        if back_btn:
            back_btn.show()
        for btn in self.main_footer.findChildren(QPushButton):
            if "upload" in btn.objectName().lower() or "upload" in btn.text().lower():
                btn.hide()
        self.play_sound("click-button.wav")

    def start_game_mode(self):
        """Entry point for Game Mode. Always runs warmup fresh — no persistence."""
        print("[DEBUG] Entered start_game_mode() — launching warmup")
        self._launch_warmup()

    # ── Warmup launch helpers ────────────────────────────────────────────────

    def _launch_warmup(self):
        """Show the warmup intro screen."""
        print("[DEBUG] Entered _launch_warmup()")
        try:
            from pages.warmup_ui import WarmupIntroWidget
            from pages.shared_ui import apply_theme
            if hasattr(self, 'tts'):
                self.tts.stop()

            # Clear any previous warmup session so results don't bleed between plays
            if hasattr(self, '_warmup_session'):
                del self._warmup_session

            self._warmup_intro_widget = WarmupIntroWidget(
                on_begin=self._begin_warmup_questions,
                window=self,
                tts=self.tts,
            )
            apply_theme(self._warmup_intro_widget, self.current_theme)
            self._switch_to_page(self._warmup_intro_widget)

            self.main_footer.show()
            self.section_footer.hide()
            back_btn = self.main_footer.findChild(QPushButton, tr("Back to Menu").lower().replace(" ", "_"))
            if back_btn:
                back_btn.show()
            for btn in self.main_footer.findChildren(QPushButton):
                if "upload" in btn.objectName().lower() or "upload" in btn.text().lower():
                    btn.hide()
        except Exception as e:
            import traceback
            print(f"[CRASH] Exception in _launch_warmup: {e}")
            traceback.print_exc()

    def _begin_warmup_questions(self):
        """Transition from intro screen to the question widget."""
        print("[DEBUG] Entered _begin_warmup_questions()")
        try:
            from question.warmup import WarmupSession
            from pages.warmup_ui import WarmupQuestionWidget
            from pages.shared_ui import apply_theme

            self._warmup_session = WarmupSession()
            self._warmup_question_widget = WarmupQuestionWidget(
                session=self._warmup_session,
                window=self,
                tts=self.tts,
                on_complete=self._show_warmup_ranking,
            )
            apply_theme(self._warmup_question_widget, self.current_theme)
            self._switch_to_page(self._warmup_question_widget)

            self.main_footer.hide()
            for btn in self.section_footer.findChildren(QPushButton):
                btn.show()
            back_ops = self.section_footer.findChild(QPushButton, "back_to_operations")
            if back_ops: back_ops.hide()
            back_learn = self.section_footer.findChild(QPushButton, "back_to_learn")
            if back_learn: back_learn.hide()
            self.section_footer.show()
        except Exception as e:
            import traceback
            print(f"[CRASH] Exception in _begin_warmup_questions: {e}")
            traceback.print_exc()

    def _show_warmup_ranking(self):
        """Show the ranked results screen. Ranked list stays in memory only."""
        from pages.warmup_ui import WarmupRankingWidget
        from pages.shared_ui import apply_theme

        if hasattr(self, '_warmup_question_widget'):
            self._warmup_question_widget.cleanup()

        ranked = self._warmup_session.get_ranked_results()
        print(f"[WARMUP] Complete. Top skill: {ranked[0]['label'] if ranked else 'N/A'}")

        self._warmup_ranking_widget = WarmupRankingWidget(
            session=self._warmup_session,
            window=self,
            tts=self.tts,
            on_continue=self._on_warmup_complete,
        )
        apply_theme(self._warmup_ranking_widget, self.current_theme)
        self._switch_to_page(self._warmup_ranking_widget)

        self.main_footer.show()
        self.section_footer.hide()
        back_btn = self.main_footer.findChild(QPushButton, tr("Back to Menu").lower().replace(" ", "_"))
        if back_btn:
            back_btn.show()
        for btn in self.main_footer.findChildren(QPushButton):
            if "upload" in btn.objectName().lower() or "upload" in btn.text().lower():
                btn.hide()

    def _on_warmup_complete(self):
        """Called when user presses Continue on the ranking screen."""
        if hasattr(self, '_warmup_ranking_widget'):
            self._warmup_ranking_widget.cleanup()
        self._launch_game_mode_intro()

    # ── Game Mode (adaptive) ────────────────────────────────────────────────

    def _launch_game_mode_intro(self):
        """Show the brief intro screen before starting a game session."""
        from pages.warmup_ui import GameModeIntroWidget
        from pages.shared_ui import apply_theme
        if hasattr(self, 'tts'): self.tts.stop()

        # Pull ranked from the live warmup session — no disk reads
        ranked = self._warmup_session.get_ranked_results() if hasattr(self, '_warmup_session') else []

        self._gamemode_intro = GameModeIntroWidget(
            ranked=ranked, saved_state=None,
            on_start=self._start_game_session,
            window=self, tts=self.tts,
        )
        apply_theme(self._gamemode_intro, self.current_theme)
        self._switch_to_page(self._gamemode_intro)

        self.main_footer.show()
        self.section_footer.hide()
        back_btn = self.main_footer.findChild(QPushButton, tr("Back to Menu").lower().replace(" ", "_"))
        if back_btn: back_btn.show()
        for btn in self.main_footer.findChildren(QPushButton):
            if "upload" in btn.objectName().lower() or "upload" in btn.text().lower():
                btn.hide()

    def _start_game_session(self):
        """Create GameModeSession + GameModeWidget, start 90s timer."""
        from question.warmup import GameModeSession
        from pages.warmup_ui import GameModeWidget
        from pages.shared_ui import apply_theme
        if hasattr(self, 'tts'): self.tts.stop()

        # Pull ranked from the live warmup session — no disk reads
        ranked = self._warmup_session.get_ranked_results() if hasattr(self, '_warmup_session') else []

        self._game_session_new = GameModeSession(ranked)
        self.time_remaining    = self._game_session_new.session_time
        self.game_active       = True

        if not hasattr(self, 'game_page_container'):
            self.game_page_container = QWidget()
            self.game_page_layout    = QVBoxLayout(self.game_page_container)
            self.game_page_layout.setContentsMargins(0, 0, 0, 0)

        clear_layout(self.game_page_layout)

        self.game_mode_widget = GameModeWidget(
            session=self._game_session_new,
            window=self, tts=self.tts,
            on_session_end=self._on_game_mode_end,
        )
        apply_theme(self.game_mode_widget, self.current_theme)
        self.game_page_layout.addWidget(self.game_mode_widget)
        self._switch_to_page(self.game_page_container)

        self.main_footer.hide()
        self.section_footer.show()
        back_ops = self.section_footer.findChild(QPushButton, "back_to_operations")
        if back_ops: back_ops.hide()
        back_learn = self.section_footer.findChild(QPushButton, "back_to_learn")
        if back_learn: back_learn.hide()
        for btn in self.section_footer.findChildren(QPushButton):
            if "upload" in btn.objectName().lower() or "upload" in btn.text().lower():
                btn.hide()

        self._original_back_to_home = self.back_to_home
        def safe_back():
            if hasattr(self, 'game_timer') and self.game_timer.isActive(): self.game_timer.stop()
            self.game_active = False
            if hasattr(self, 'tts'): self.tts.stop()
            if hasattr(self, 'game_mode_widget'): self.game_mode_widget.cleanup()
            if hasattr(self, '_original_back_to_home'): self.back_to_home = self._original_back_to_home
            self.back_to_main_menu()
        self.back_to_home = safe_back

        if hasattr(self, 'tts') and not self.is_muted:
            QTimer.singleShot(300, lambda: self.tts.speak(tr("Game mode! Let's go!")))

        self.game_timer.start()

    def _on_game_mode_end(self):
        """Called by GameModeWidget when session finishes (timer or no more questions)."""
        if not self.game_active: return
        self.game_active = False
        self.game_timer.stop()
        if hasattr(self, 'tts'): self.tts.stop()
        if hasattr(self, '_original_back_to_home'): self.back_to_home = self._original_back_to_home

        print(f"[GAME] Session ended. Q={self._game_session_new.question_count} Acc={self._game_session_new.accuracy_pct()}%")
        QTimer.singleShot(500, lambda: self.tts.speak(tr("Time's up! Amazing effort.")))
        QTimer.singleShot(2200, self._show_game_report)

    def _show_game_report(self):
        from pages.warmup_ui import GameModeReportWidget
        from pages.shared_ui import apply_theme
        report = GameModeReportWidget(
            session=self._game_session_new, window=self, tts=self.tts,
            on_play_again=self._on_game_play_again,
        )
        apply_theme(report, self.current_theme)
        self._switch_to_page(report)
        self.section_footer.hide()
        self.main_footer.show()
        back_btn = self.main_footer.findChild(QPushButton, tr("Back to Menu").lower().replace(" ", "_"))
        if back_btn: back_btn.show()
        for btn in self.main_footer.findChildren(QPushButton):
            if "upload" in btn.objectName().lower() or "upload" in btn.text().lower(): btn.hide()

    def _on_game_play_again(self):
        """Play Again: go back to warmup for a fresh session."""
        self._launch_warmup()

    def load_game_questions(self, difficulty_index):
        from question.loader import LinearProgressionSession, QuestionProcessor
        from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QWidget, QPushButton
        from PyQt5.QtCore import QTimer, Qt
        from language.language import tr

        if hasattr(self, 'tts'):
            self.tts.stop()

        if not hasattr(self, 'game_page_container'):
            self.game_page_container = QWidget()
            self.game_page_layout = QVBoxLayout(self.game_page_container)
            self.game_page_layout.setContentsMargins(0, 0, 0, 0)

        clear_layout(self.game_page_layout)

        self.game_session = LinearProgressionSession(difficulty_index)
        self.time_remaining = 90
        self.game_active = True

        self.timer_bar = QProgressBar()
        self.timer_bar.setMaximum(self.game_session.session_time)
        self.timer_bar.setMinimum(0)
        self.timer_bar.setValue(self.game_session.session_time)
        self.timer_bar.setTextVisible(True)
        self.timer_bar.setFormat("%vs")
        self.timer_bar.setAccessibleName("")
        self.timer_bar.setAccessibleDescription("")
        self.game_page_layout.addWidget(self.timer_bar)

        self.game_timer.start()

        if hasattr(self, 'tts') and not self.is_muted:
            self.tts.speak(tr("Game mode! Let's go!"))

        processor = self.game_session.get_next_question()

        def load_next_question():
            if not self.game_active:
                return

            result = getattr(self.question_widget, '_last_result', None)
            if result:
                self.question_widget._last_result = None
                self.game_session.submit_answer(
                    result['skill'],
                    result['correct'],
                    result['elapsed'],
                    result.get('replay_count', 0)
                )
                self._log_diagnostics()

            if self.game_session.is_session_complete():
                self._end_game_session()
                return

            next_processor = self.game_session.get_next_question()
            self.question_widget.processor = next_processor
            self.question_widget.load_new_question()

        from pages.shared_ui import QuestionWidget
        self.question_widget = QuestionWidget(processor, window=self, next_question_callback=load_next_question, tts=self.tts)
        self.game_page_layout.addWidget(self.question_widget)

        self.stack.setCurrentWidget(self.game_page_container)

        if hasattr(self, 'section_footer'):
            self.main_footer.hide()
            self.section_footer.show()
            back_ops = self.section_footer.findChild(QPushButton, "back_to_operations")
            if back_ops: back_ops.hide()
            back_learn = self.section_footer.findChild(QPushButton, "back_to_learn")
            if back_learn: back_learn.hide()

            for btn in self.section_footer.findChildren(QPushButton):
                if "upload" in btn.objectName().lower() or "upload" in btn.text().lower():
                    btn.hide()

            self._original_back_to_home = self.back_to_home

            def safe_back_to_home():
                if hasattr(self, 'game_timer') and self.game_timer.isActive():
                    self.game_timer.stop()
                if hasattr(self, 'game_active'):
                    self.game_active = False
                if hasattr(self, 'tts'):
                    self.tts.stop()
                if hasattr(self, 'question_widget'):
                    self.question_widget.stop_all_activity()
                if hasattr(self, '_original_back_to_home'):
                    self.back_to_home = self._original_back_to_home
                self._cleanup_game_footer()
                self.back_to_main_menu()

            self.back_to_home = safe_back_to_home

            back_to_diff_btn = QPushButton(tr("Back to Difficulty"))
            back_to_diff_btn.setObjectName("back_to_difficulty")
            back_to_diff_btn.setProperty("class", "footer-button")
            back_to_diff_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
            back_to_diff_btn.adjustSize()
            back_to_diff_btn.setFont(QFont("Arial", 14))
            back_to_diff_btn.setAccessibleName(tr("Back to Difficulty"))
            back_to_diff_btn.setAccessibleDescription(tr("Return to difficulty selection"))
            back_to_diff_btn.clicked.connect(self._back_to_difficulty)

            from pages.shared_ui import apply_theme
            apply_theme(back_to_diff_btn, self.current_theme)

            back_ops = self.section_footer.findChild(QPushButton, "back_to_operations")
            back_home = self.section_footer.findChild(QPushButton, "back_to_home")

            if back_ops:
                idx = self.section_footer.layout().indexOf(back_ops)
            elif back_home:
                idx = self.section_footer.layout().indexOf(back_home)
            else:
                idx = 2

            self.section_footer.layout().insertWidget(idx, back_to_diff_btn)
            self._back_to_diff_btn = back_to_diff_btn

    def _cleanup_game_footer(self):
        if hasattr(self, '_back_to_diff_btn') and self._back_to_diff_btn:
            self._back_to_diff_btn.setParent(None)
            self._back_to_diff_btn = None

    def _update_timer_bar(self):
        self.timer_bar.setValue(self.time_remaining)
        if self.time_remaining > 30:
            color = "#1D9E75"
        elif self.time_remaining > 15:
            color = "#EF9F27"
        else:
            color = "#E24B4A"
        self.timer_bar.setStyleSheet(f"QProgressBar::chunk {{ background-color: {color}; border-radius: 4px; }}")

    def _log_diagnostics(self):
        session = self.game_session
        print(f"[GAME] State: {session.state}")
        print(f"[GAME] Phase: {session.phase}")
        print(f"[GAME] Question: {session.question_count}")
        print(f"[GAME] Skill scores: {session.skill_scores}")

    def _get_difficulty_name(self, index):
        levels = ["Easy", "Medium", "Hard", "Extra Hard"]
        if 0 <= index < len(levels):
            from language.language import tr
            return tr(levels[index])
        return ""

    def _on_game_tick(self):
        self.time_remaining -= 1
        if hasattr(self, 'game_mode_widget') and self.game_mode_widget:
            try: self.game_mode_widget.update_timer(self.time_remaining)
            except Exception: pass
        elif hasattr(self, 'timer_bar'):
            self._update_timer_bar()

        from language.language import tr
        if self.time_remaining == 15:
            self.tts.speak(tr("Keep going!"))
        elif self.time_remaining == 5:
            self.tts.speak(tr("One more!"))
        elif self.time_remaining <= 0:
            if hasattr(self, 'game_mode_widget') and self.game_mode_widget:
                self._on_game_mode_end()
            else:
                self._end_game_session()

    def _end_game_session(self):
        if not self.game_active:
            return
        self.game_active = False
        self.game_timer.stop()
        self.tts.stop()
        self.question_widget.stop_all_activity()

        if hasattr(self, '_original_back_to_home'):
            self.back_to_home = self._original_back_to_home

        from language.language import tr
        print(f"[GAME] Session ended. Final scores: {self.game_session.skill_scores}")

        QTimer.singleShot(500, lambda: self.tts.speak(tr("Time's up! Amazing effort.")))
        QTimer.singleShot(2500, self.show_end_report)

    def show_end_report(self):
        from pages.shared_ui import GameReportWidget, apply_theme
        from language.language import tr

        self._cleanup_game_footer()
        report = GameReportWidget(session=self.game_session, window=self, tts=self.tts)
        apply_theme(report, self.current_theme)

        self.stack.addWidget(report)
        self.stack.setCurrentWidget(report)

        if hasattr(self, 'section_footer'): self.section_footer.hide()
        if hasattr(self, 'main_footer'): self.main_footer.show()
        back_btn = self.main_footer.findChild(QPushButton, tr("Back to Menu").lower().replace(" ", "_"))
        if back_btn: back_btn.show()

        upload_btn = self.main_footer.findChild(QPushButton, tr("Upload").lower().replace(" ", "_"))
        if upload_btn: upload_btn.hide()

    def start_quickplay_mode(self):
        self._proceed_to_quickplay()

    def _proceed_to_quickplay(self):
        if hasattr(self, 'tts'):
            self.tts.stop()

        self.main_footer.show()
        self.section_footer.hide()

        upload_btn = self.main_footer.findChild(QPushButton, tr("Upload").lower().replace(" ", "_"))
        if upload_btn:
            upload_btn.hide()

        back_btn = self.main_footer.findChild(QPushButton, tr("Back to Menu").lower().replace(" ", "_"))
        if back_btn:
            back_btn.show()

        if not hasattr(self, "quickplay_container"):
            self.quickplay_container = QWidget()
            self.quickplay_container.setAccessibleName("")
            self.quickplay_container.setAccessibleDescription("")
            quickplay_layout = QVBoxLayout()
            self.quickplay_container.setLayout(quickplay_layout)
            self.stack.addWidget(self.quickplay_container)

        if hasattr(self, '_quickplay_question_widget') and self._quickplay_question_widget:
            processor = QuestionProcessor("Story", difficultyIndex=[0, 1])
            self._quickplay_question_widget.processor = processor
            self._quickplay_question_widget.load_new_question()
            self.stack.setCurrentWidget(self.quickplay_container)
            return

        processor = QuestionProcessor("Story", difficultyIndex=[0, 1])

        def load_next_question():
            new_processor = QuestionProcessor("Story", difficultyIndex=[0, 1])
            self._quickplay_question_widget.processor = new_processor
            self._quickplay_question_widget.load_new_question()

        self._quickplay_question_widget = QuestionWidget(processor, window=self, next_question_callback=load_next_question, tts=self.tts)
        self.quickplay_container.layout().addWidget(self._quickplay_question_widget)
        self.stack.setCurrentWidget(self.quickplay_container)
        apply_theme(self.quickplay_container, self.current_theme)

    def play_sound(self, filename):
        if self.is_muted:
            return

        if filename.startswith("tts_cache_"):
            try:
                sounds_dir = "sounds"
                for f in os.listdir(sounds_dir):
                    if f.startswith("tts_cache_") and f != filename:
                        os.remove(os.path.join(sounds_dir, f))
            except Exception:
                pass

        filepath = os.path.abspath(os.path.join("sounds", filename))
        if os.path.exists(filepath):
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(filepath)))
            self.media_player.play()
        else:
            print(f"[SOUND ERROR] File not found: {filepath}")

    def play_background_music(self):
        if self.is_muted:
            return

        filepath = os.path.abspath(os.path.join("sounds", "backgroundmusic.mp3"))
        if os.path.exists(filepath):
            self.bg_player.setMedia(QMediaContent(QUrl.fromLocalFile(filepath)))
            self.bg_player.setVolume(10)
            self.bg_player.play()
            if not getattr(self, '_bg_loop_connected', False):
                self.bg_player.mediaStatusChanged.connect(self.loop_background_music)
                self._bg_loop_connected = True
        else:
            print("[BG MUSIC ERROR] File not found:", filepath)

    def loop_background_music(self, status):
        if status == QMediaPlayer.EndOfMedia:
            self.bg_player.setPosition(0)
            self.bg_player.play()

    def create_audio_button(self):
        self.audio_button = QPushButton("🔊")
        self.audio_button.setObjectName("audio-button")
        self.audio_button.setToolTip("Toggle Mute/Unmute")
        self.audio_button.clicked.connect(self.toggle_audio)
        self.audio_button.setProperty("class", "footer-button")
        self.audio_button.setFocusPolicy(Qt.StrongFocus)
        self.audio_button.setAccessibleName("Audio Unmuted")
        self.audio_button.setAccessibleDescription("Toggle mute and unmute for sounds and music")
        return self.audio_button

    def set_mute(self, state: bool):
        self.is_muted = state
        if hasattr(self, 'bg_player') and self.bg_player is not None:
            if state:
                self.bg_player.pause()
            else:
                self.play_background_music()

    def toggle_audio(self):
        new_state = not self.is_muted
        self.set_mute(new_state)

        icon_text = "🔇" if new_state else "🔊"
        accessible_name = "Audio Muted" if new_state else "Audio Unmuted"

        for btn in self.findChildren(QPushButton, "audio-button"):
            btn.setText(icon_text)
            btn.setAccessibleName(accessible_name)

        print("[AUDIO]", "Muted" if new_state else "Unmuted")

    def create_buttons(self):
        button_grid = QGridLayout()
        button_grid.setSpacing(20)
        button_grid.setContentsMargins(10, 10, 10, 10)

        sections = ["Story", "Time", "Currency", "Distance", "Bellring", "Operations"]
        self.menu_buttons = []

        for i, name in enumerate(sections):
            translated_name = tr(name)
            button = QPushButton(translated_name)
            button.setMinimumSize(250, 65)
            button.setMaximumSize(300, 75)
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            button.setProperty("class", "menu-button")
            button.setAccessibleName(translated_name)
            button.clicked.connect(lambda checked, n=name: self.load_section(n))

            self.menu_buttons.append(button)
            row, col = divmod(i, 2)
            button_grid.addWidget(button, row, col)

        return button_grid

    def create_section_footer(self):
        buttons = ["Back to Operations", "Back to Learn", "Back to Home", "Settings"]
        translated = [tr(b) for b in buttons]

        callbacks = {
            tr("Back to Operations"): lambda: self.load_section("Operations"),
            tr("Back to Learn"): self.back_to_learn_menu,
            tr("Back to Home"): lambda: self.back_to_home(),
            tr("Settings"): self.handle_settings
        }

        footer = create_footer_buttons(translated, callbacks=callbacks)

        audio_btn = self.create_audio_button()
        footer.layout().insertWidget(0, audio_btn, alignment=Qt.AlignLeft)

        for btn in footer.findChildren(QPushButton):
            if btn.text() == tr("Back to Operations"):
                btn.setObjectName("back_to_operations")
            elif btn.text() == tr("Back to Learn"):
                btn.setObjectName("back_to_learn")
            elif btn.text() == tr("Back to Home"):
                btn.setObjectName("back_to_home")

        return footer

    def handle_settings(self):
        dialog = SettingsDialog(
            parent=self,
            initial_difficulty=getattr(self, "current_difficulty", 1),
            main_window=self
        )

        if dialog.exec_() == QDialog.Accepted:
            self.current_difficulty = dialog.get_difficulty_index()
            new_language = dialog.get_selected_language()
            if new_language != self.language:
                self.refresh_ui(new_language)

    def load_section(self, name):
        if hasattr(self, 'tts'):
            self.tts.stop()
        print(f"[INFO] Loading section: {name}")

        page = load_pages(name, self.back_to_main_menu, difficulty_index=self.current_difficulty, main_window=self, tts=self.tts)

        if hasattr(self, "current_theme"):
            page.style().unpolish(page)
            page.style().polish(page)
            apply_theme(page, self.current_theme)

        if name in self.section_pages:
            old_page = self.section_pages[name]
            if not sip.isdeleted(old_page):
                self.stack.removeWidget(old_page)
                old_page.deleteLater()
            del self.section_pages[name]

        self.section_pages[name] = page
        self.stack.addWidget(page)

        self.stack.setCurrentWidget(page)
        self.menu_widget.hide()
        self.main_footer.hide()
        self.section_footer.show()
        self.update_back_to_operations_visibility(name)

    def back_to_main_menu(self):
        self.top_bar.show()

        for attr in ('_warmup_question_widget', '_warmup_intro_widget', '_warmup_ranking_widget'):
            widget = getattr(self, attr, None)
            if widget:
                try:
                    widget.cleanup()
                except Exception:
                    pass

        current_page = self.stack.currentWidget()
        if current_page:
            question_widget = current_page.findChild(QuestionWidget)
            if question_widget:
                question_widget.stop_all_activity()

        if hasattr(self, 'tts'):
            self.tts.stop()
            self.tts.reset()
        self.play_sound("home_button_sound.wav")
        self.stack.setCurrentWidget(self.startup_widget)
        self.section_footer.hide()
        self.main_footer.show()

        for btn in self.main_footer.findChildren(QPushButton):
            if "upload" in btn.objectName().lower() or "upload" in btn.text().lower():
                btn.show()

        back_btn = self.main_footer.findChild(QPushButton, tr("Back to Menu").lower().replace(" ", "_"))
        if back_btn:
            back_btn.hide()
        self.focus_quickplay_button()

    def back_to_learn_menu(self):
        from pages.shared_ui import QuestionWidget

        current_page = self.stack.currentWidget()
        if current_page:
            question_widget = current_page.findChild(QuestionWidget)
            if question_widget:
                question_widget.stop_all_activity()

        if hasattr(self, 'tts'):
            self.tts.stop()
            self.tts.reset()

        self.stack.setCurrentWidget(self.menu_widget)
        self.section_footer.hide()
        self.main_footer.show()

    def back_to_home(self):
        current_page = self.stack.currentWidget()

        if hasattr(self, 'game_page_container') and current_page == self.game_page_container:
            if hasattr(self, 'game_timer') and self.game_timer.isActive():
                self.game_timer.stop()
            if hasattr(self, 'game_active'):
                self.game_active = False
            if hasattr(self, 'tts'):
                self.tts.stop()
            if hasattr(self, 'question_widget'):
                self.question_widget.stop_all_activity()
            if hasattr(self, '_cleanup_game_footer'):
                self._cleanup_game_footer()
            self.back_to_main_menu()
            return

        if current_page:
            question_widget = current_page.findChild(QuestionWidget)
            if question_widget:
                question_widget.stop_all_activity()

        if hasattr(self, 'tts'):
            self.tts.stop()
            self.tts.reset()

        self.back_to_main_menu()

    def clear_main_layout(self):
        for i in reversed(range(self.main_layout.count())):
            widget = self.main_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

    def handle_upload(self):
        upload_excel(self)

    def load_style(self, qss_file):
        path = os.path.join("styles", qss_file)
        if os.path.exists(path):
            with open(path, "r") as f:
                self.base_qss = f.read()
                self.setStyleSheet(self.base_qss)

    def update_dynamic_styles(self):
        width_scale = self.width() / 900.0 if self.width() > 0 else 1.0
        height_scale = self.height() / 600.0 if self.height() > 0 else 1.0
        scale = min(width_scale, height_scale)

        if scale < 0.82:
            scale = 0.82

        footer_font_size = 17 * scale
        button_font_size = 18 * scale
        if getattr(self, 'language', '') == "മലയാളം":
            footer_font_size = 14 * scale
            button_font_size = 16 * scale

        dynamic_css = f"""
        QWidget {{ font-size: {int(16 * scale)}px; }}
        QLabel[class="main-title"] {{ font-size: {int(28 * scale)}px; }}
        QLabel[class="subtitle"] {{ font-size: {int(20 * scale)}px; }}
        QLabel[class="question-label"] {{ font-size: {int(28 * scale)}px; }}
        QLineEdit.answer-input {{ font-size: {int(24 * scale)}px; }}
        QPushButton[theme="light"] {{ 
            font-size: {int(button_font_size)}px; 
            padding: {int(12 * scale)}px {int(20 * scale)}px; 
        }}
        QPushButton[theme="dark"] {{ 
            font-size: {int(button_font_size)}px; 
            padding: {int(12 * scale)}px {int(20 * scale)}px; 
        }}
        QPushButton.footer-button {{ 
            font-size: {int(footer_font_size)}px; 
            padding: {int(8 * scale)}px {int(12 * scale)}px; 
        }}
        QComboBox.combo-box {{ font-size: {int(19 * scale)}px; }}
        """
        self.setStyleSheet(getattr(self, 'base_qss', '') + dynamic_css)

        for btn in self.findChildren(QPushButton):
            if not sip.isdeleted(btn) and btn.property("class") == "menu-button":
                max_width = int(340 * scale) if getattr(self, 'language', '') == "മലയാളം" else int(280 * scale)
                btn.setMaximumSize(max_width, int(75 * scale))

        for qwidget in self.findChildren(QuestionWidget):
            if not sip.isdeleted(qwidget):
                qwidget.update_scaling(scale)

        if hasattr(self, '_welcome_movie') and self._welcome_movie:
            if hasattr(self, 'gif_label') and self.gif_label:
                target_size = int(280 * (self.height() / 600.0))
                target_size = min(max(200, target_size), 450)
                self._welcome_movie.setScaledSize(QSize(target_size, target_size))
                self.gif_label.setFixedSize(target_size, target_size)

        if hasattr(self, 'main_footer') and self.main_footer:
            self.main_footer.setMinimumHeight(int(65 * scale))
        if hasattr(self, 'section_footer') and self.section_footer:
            self.section_footer.setMinimumHeight(int(65 * scale))

        if hasattr(self, 'learn_mode_layout_box'):
            if self.width() < 950:
                self.learn_mode_layout_box.setDirection(QBoxLayout.TopToBottom)
            else:
                self.learn_mode_layout_box.setDirection(QBoxLayout.LeftToRight)

        if hasattr(self, 'movie_learn') and self.movie_learn:
            if hasattr(self, 'gif_label_learn') and self.gif_label_learn:
                target_size = int(240 * scale)
                target_size = min(max(200, target_size), 450)
                self.movie_learn.setScaledSize(QSize(target_size, target_size))
                self.gif_label_learn.setFixedSize(target_size, target_size)

    def toggle_theme(self):
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        print("Theme switched to:", self.current_theme)
        self.theme_button.setText("☀️" if self.current_theme == "dark" else "🌙")
        self.theme_button.setAccessibleName(f"Toggle theme. Currently {self.current_theme} mode")
        apply_theme(self.central_widget, self.current_theme)

    def update_back_to_operations_visibility(self, section_name):
        operation_subsections = {
            "addition", "subtraction", "multiplication",
            "division", "remainder", "percentage"
        }
        normalized = section_name.strip().lower()
        back_to_ops_btn = self.section_footer.findChild(QPushButton, "back_to_operations")
        if back_to_ops_btn:
            back_to_ops_btn.setVisible(normalized in operation_subsections)


if __name__ == "__main__":

    app = QApplication(sys.argv)
    style_file = os.path.join("styles", "app.qss")
    if os.path.exists(style_file):
        with open(style_file, "r") as f:
            app.setStyleSheet(f.read())

    lang = get_saved_language()
    if lang:
        print("Saved language found:", lang)
        window = MainWindow(language=lang)
        window.show()
        window.activateWindow()
        window.raise_()
        sys.exit(app.exec_())
    else:
        dialog = RootWindow()
        if dialog.exec_() == QDialog.Accepted:
            window = MainWindow(language=dialog.language_combo.currentText())
            window.show()
            window.activateWindow()
            window.raise_()
            sys.exit(app.exec_())