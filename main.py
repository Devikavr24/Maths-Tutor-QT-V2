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
from PyQt5.QtCore import Qt,QUrl, QSize, QTimer
from question.loader import QuestionProcessor
from pages.shared_ui import create_footer_buttons, apply_theme, SettingsDialog, create_main_footer_buttons,QuestionWidget,setup_exit_handling 
from pages.ques_functions import load_pages, upload_excel   
from tts.tts_worker import TextToSpeech

from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

from language.language import get_saved_language, save_selected_language_to_file, tr, set_language

from PyQt5.QtGui import QMovie, QKeySequence, QPixmap, QFont, QIcon
from PyQt5.QtCore import Qt



class RootWindow(QDialog):
    def __init__(self,minimal=False):
        super().__init__()
        self.minimal = minimal
        self.remember=False
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
        
        # ✅ BUG FIX: Set global language on startup so it applies everywhere
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
        self.base_qss = ""  # For dynamic scaling
        self.load_style("main_window.qss")
        self.current_theme = "light"  


        self.media_player = QMediaPlayer()
        self.bg_player = QMediaPlayer()
        self.bg_player.setVolume(30)
        self.is_muted = False 
        self.play_background_music()

        self.difficulty_index = 1 

        # Ctrl+; shortcut to decrease speed / re-read question
        self._slower_shortcut = QShortcut(QKeySequence("Ctrl+;"), self)
        self._slower_shortcut.activated.connect(self._on_slower)
        
        # Alt+; shortcut to increase speed
        self._faster_shortcut = QShortcut(QKeySequence("Alt+;"), self)
        self._faster_shortcut.activated.connect(self._on_faster)

        # Ctrl+R shortcut to repeat question
        self._repeat_shortcut = QShortcut(QKeySequence("Ctrl+R"), self)
        self._repeat_shortcut.activated.connect(self._on_repeat_question)

    def refresh_ui(self, new_language):
        """Rebuilds the entire UI with the new language WITHOUT closing the window."""
        print(f"[System] Refreshing UI to {new_language}...")
        
        # ✅ BUG FIX: Ensure new language is set globally before redrawing
        self.language = new_language
        set_language(new_language)
        
        self.setWindowTitle(f"Maths Tutor - {self.language}")

        if hasattr(self, 'tts'):
            self.tts.stop()
        
        # ✅ BUG FIX: Clear stale widget references before init_ui destroys old central widget
        self.section_pages = {}
        if hasattr(self, 'game_mode_container'):
            del self.game_mode_container
        if hasattr(self, '_quickplay_question_widget'):
            del self._quickplay_question_widget
        if hasattr(self, 'quickplay_container'):
            del self.quickplay_container
        
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

        menu_layout.addStretch() # Top centering spacer

        title = QLabel(tr("🎓 Learning Mode"))
        title.setAlignment(Qt.AlignCenter)
        title.setProperty("class", "main-title")
        menu_layout.addWidget(title, alignment=Qt.AlignCenter)
            # Side-by-side layout for Content (fits down to minimum size with 2 columns)
        self.learn_mode_layout = QHBoxLayout()
        self.learn_mode_layout.setSpacing(40)
        self.learn_mode_layout.setAlignment(Qt.AlignCenter)
 
        # GIF Container
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
         
        # Buttons Grid Wrapper
        self.buttons_learn_widget = QWidget()
        self.buttons_learn_widget.setLayout(self.create_buttons())
 
        self.learn_mode_layout.addWidget(self.gif_learn_container, alignment=Qt.AlignCenter)
        self.learn_mode_layout.addWidget(self.buttons_learn_widget, alignment=Qt.AlignCenter)
 
        menu_layout.addLayout(self.learn_mode_layout)
        menu_layout.addStretch() # Bottom centering spacer

        self.stack = QStackedWidget()
        self.stack.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.stack.setAccessibleName("Content area")

        self.startup_widget = self.create_mode_selection_page()
        self.stack.addWidget(self.startup_widget)  
        
        self.stack.addWidget(self.menu_widget)     

        self.stack.setCurrentWidget(self.startup_widget)

        self.main_layout.addWidget(self.stack)

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
        """Find and return the current question text, or None."""
        current_page = self.stack.currentWidget()
        if current_page:
            question_widget = current_page.findChild(QuestionWidget)
            if question_widget and hasattr(question_widget, 'label'):
                text = question_widget.label.text()
                if text:
                    return text
        return None

    def _on_repeat_question(self):
        """Ctrl+R : Repeat the current question text."""
        question_text = self._get_question_text()
        if question_text:
            if hasattr(self, 'tts'):
                self.tts.speak(question_text)
                print(f"[Ctrl+R] Repeating question: {question_text}")

    def _on_slower(self):
        """Ctrl+; : If TTS is speaking, decrease speed. If idle, re-read question slower."""
        step = self.tts.RATE_STEP
        current_rate = self.tts.speech_rate
        new_rate = max(50, current_rate - step)
        
        if self.tts.is_speaking:
            # TTS is active: just decrease speed
            if new_rate != current_rate:
                self.tts.set_rate(new_rate)
                print(f"[Alt+;] Speed decreased: {new_rate} WPM")
        else:
            # TTS is idle: decrease speed and re-read the question
            if new_rate != current_rate:
                self.tts.set_rate(new_rate)
            question_text = self._get_question_text()
            if question_text:
                self.tts.speak(question_text)
                print(f"[Alt+;] Re-reading at {self.tts.speech_rate} WPM: {question_text}")

    def _on_faster(self):
        """Alt+; : If TTS is speaking, increase speed. If idle, increase (capped) and re-read."""
        step = self.tts.RATE_STEP
        default = self.tts.DEFAULT_RATE
        current_rate = self.tts.speech_rate
        
        if self.tts.is_speaking:
            # TTS is active: increase speed (up to max 300)
            new_rate = min(300, current_rate + step)
            if new_rate != current_rate:
                self.tts.set_rate(new_rate)
                print(f"[Alt+;] Speed increased: {new_rate} WPM")
        else:
            # TTS is idle: increase but cap at default + 1 step, then re-read
            max_idle_rate = default + step
            new_rate = min(max_idle_rate, current_rate + step)
            if new_rate != current_rate:
                self.tts.set_rate(new_rate)
            question_text = self._get_question_text()
            if question_text:
                self.tts.speak(question_text)
                print(f"[Alt+;] Re-reading at {self.tts.speech_rate} WPM: {question_text}")

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

        #Welcome to Maths Tutor!
        title = QLabel(tr("welcome"))
        title.setAlignment(Qt.AlignCenter)
        title.setProperty("class", "main-title")
        layout.addWidget(title, alignment=Qt.AlignCenter)

        #Ready to learn...
        subtitle = QLabel(tr("ready").format(lang=self.language))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setProperty("class", "subtitle")
        layout.addWidget(subtitle, alignment=Qt.AlignCenter)
        layout.addSpacing(30) # More space for split layout 

        #Content Layout, gif+buttons sidebyside
        content_layout = QHBoxLayout()
        content_layout.setSpacing(60) 
        content_layout.setAlignment(Qt.AlignCenter)
        
        #Leftmost Gif
        gif_label = QLabel()
        gif_label.setAlignment(Qt.AlignCenter)
        movie = QMovie("images/welcome-1.gif")
        movie.setScaledSize(QSize(280, 280)) 
        gif_label.setMovie(movie)
        movie.start()
        self._welcome_movie = movie # Keep reference
        content_layout.addWidget(gif_label, alignment=Qt.AlignCenter)

        #Right- Buttons list
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
        
        # Add side-by-side layout to main page
        layout.addLayout(content_layout)

        return widget

    def start_learning_mode(self):
        self.stack.setCurrentWidget(self.menu_widget)
        self.main_footer.show()
        self.section_footer.hide()
        back_btn = self.main_footer.findChild(QPushButton, tr("Back to Menu").lower().replace(" ", "_"))
        if back_btn:
            back_btn.show()
        self.play_sound("click-button.wav")

    def start_game_mode(self):
        if hasattr(self, "game_mode_container"):
            self.stack.setCurrentWidget(self.game_mode_container)
            self.main_footer.show()      
            self.section_footer.hide()   
            back_btn = self.main_footer.findChild(QPushButton, tr("Back to Menu").lower().replace(" ", "_"))
            if back_btn:
                back_btn.show()
            return

        self.game_mode_container = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        self.game_mode_container.setLayout(layout)

        title_label = QLabel(tr("Select Game Difficulty"))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setProperty("class", "main-title")
        layout.addWidget(title_label)
        layout.addSpacing(10) #
        difficulties = [(tr("Easy"), 1), (tr("Medium"), 2), (tr("Hard"), 3), (tr("Extra Hard"), 4)]
        for text, index in difficulties:
            btn = QPushButton(text)
            btn.setMinimumSize(260, 70)
            btn.setProperty("class", "menu-button")
            btn.setProperty("theme", self.current_theme)
            btn.clicked.connect(lambda _, idx=index: self.load_game_questions(idx))
            btn.setAccessibleName(f"{text} difficulty")
            btn.setAccessibleDescription(f"Start game at {text} difficulty level")
            layout.addWidget(btn)

        mole_label = QLabel()
        mole_label.setPixmap(QPixmap("assets/mole.png").scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        mole_label.setAlignment(Qt.AlignCenter)
        mole_label.setAccessibleName("")
        mole_label.setAccessibleDescription("")
        layout.addWidget(mole_label)

        self.stack.addWidget(self.game_mode_container)
        self.stack.setCurrentWidget(self.game_mode_container)

        self.main_footer.show()
        self.section_footer.hide()   
        back_btn = self.main_footer.findChild(QPushButton, tr("Back to Menu").lower().replace(" ", "_"))
        if back_btn:
            back_btn.show()

        apply_theme(self.game_mode_container, self.current_theme)

    def load_game_questions(self, difficulty_index):
        from question.loader import GameSession, QuestionProcessor
        from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QWidget, QPushButton
        from PyQt5.QtCore import QTimer, Qt
        from language.language import tr

        if hasattr(self, 'tts'):
             self.tts.stop()

        # Create or retrieve standard game page inside stack
        if not hasattr(self, 'game_page_container'):
            self.game_page_container = QWidget()
            self.game_page_layout = QVBoxLayout(self.game_page_container)
            self.game_page_layout.setContentsMargins(0, 0, 0, 0)
            self.stack.addWidget(self.game_page_container)

        # Clear previous layout widgets on game restarted iterations
        for i in reversed(range(self.game_page_layout.count())):
            widget = self.game_page_layout.itemAt(i).widget()
            if widget: widget.setParent(None)

        self.game_session = GameSession(difficulty_index)
        self.time_remaining = 90
        self.game_active = True

        # Timer Bar Only
        self.timer_bar = QProgressBar()
        self.timer_bar.setMaximum(self.game_session.session_time)
        self.timer_bar.setMinimum(0)
        self.timer_bar.setValue(self.game_session.session_time)
        self.timer_bar.setTextVisible(True)
        self.timer_bar.setFormat("%vs")
        self.timer_bar.setAccessibleName("")
        self.timer_bar.setAccessibleDescription("")
        self.game_page_layout.addWidget(self.timer_bar)

        # Timer setup
        self.game_timer = QTimer(self)
        self.game_timer.setInterval(1000)
        self.game_timer.timeout.connect(self._on_game_tick)
        self.game_timer.start()

        if hasattr(self, 'tts') and not self.is_muted:
            self.tts.speak(tr("Game mode! Let's go!"))

        processor = self.game_session.get_next_question()
        processor.process_file() 

        def load_next_question():
            if not self.game_active:
                return

            result = getattr(self.question_widget, '_last_result', None)
            if result:
                self.game_session.submit_answer(result['skill'], result['correct'], result['elapsed'])
                self._log_diagnostics()

            if self.game_session.is_session_complete():
                self._end_game_session()
                return

            next_processor = self.game_session.get_next_question()
            next_processor.process_file()
            self.question_widget.processor = next_processor
            self.question_widget.load_new_question()
            
            # Deduplication now handled by GameSession during get_next_question



        from pages.shared_ui import QuestionWidget
        self.question_widget = QuestionWidget(processor, window=self, next_question_callback=load_next_question, tts=self.tts)
        self.game_page_layout.addWidget(self.question_widget)

        # Apply standard page switch
        self.stack.setCurrentWidget(self.game_page_container)

        # Navigation Footer overrides
        if hasattr(self, 'section_footer'):
             self.main_footer.hide()
             self.section_footer.show()
             # Hide Back to Operations
             back_ops = self.section_footer.findChild(QPushButton, "back_to_operations")
             if back_ops: back_ops.hide()

             # Bulletproof Upload button hide
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
                 self._original_back_to_home()

             self.back_to_home = safe_back_to_home

             # Add Back to Difficulty button
             back_to_diff_btn = QPushButton(tr("Difficulty"))
             back_to_diff_btn.setObjectName("back_to_difficulty")
             back_to_diff_btn.setProperty("class", "footer-button")
             back_to_diff_btn.setAccessibleName(tr("Back to Difficulty"))
             back_to_diff_btn.setAccessibleDescription(tr("Return to difficulty selection"))
             back_to_diff_btn.clicked.connect(self._back_to_difficulty)
             self.section_footer.layout().addWidget(back_to_diff_btn)
             self._back_to_diff_btn = back_to_diff_btn


    def _cleanup_game_footer(self):
        if hasattr(self, '_back_to_diff_btn') and self._back_to_diff_btn:
            self._back_to_diff_btn.setParent(None)
            self._back_to_diff_btn = None

    def _back_to_difficulty(self):
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
        
        self.stack.setCurrentWidget(self.game_mode_container)
        self.main_footer.hide()
        self.section_footer.show()
        back_ops = self.section_footer.findChild(QPushButton, "back_operations")
        if back_ops: back_ops.hide()

    def _update_timer_bar(self):
        self.timer_bar.setValue(self.time_remaining)
        if self.time_remaining > 30:
            color = "#1D9E75"   # green
        elif self.time_remaining > 15:
            color = "#EF9F27"   # amber
        else:
            color = "#E24B4A"   # red
        self.timer_bar.setStyleSheet(f"QProgressBar::chunk {{ background-color: {color}; border-radius: 4px; }}")

    def _log_diagnostics(self):
        session = self.game_session
        print(f"[GAME] State: {session.state}")
        print(f"[GAME] Phase: {session.phase}")
        print(f"[GAME] Question: {session.question_count}")
        print(f"[GAME] Skill scores: {session.skill_scores}")
        print(f"[GAME] Mistake queue: {len(session.mistake_queue)} items")

    def _get_difficulty_name(self, index):
        levels = ["Simple", "Easy", "Medium", "Hard", "Challenging"]
        if 0 <= index < len(levels):
             from language.language import tr
             return tr(levels[index])
        return ""

    def _on_game_tick(self):
        self.time_remaining -= 1
        self._update_timer_bar()
        
        from language.language import tr

        if self.time_remaining == 15:
            self.game_session.set_finale()
            self.tts.speak(tr("Keep going!"))
        elif self.time_remaining == 5:
            self.tts.speak(tr("One more!"))
        elif self.time_remaining <= 0:
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
            processor.process_file()
            self._quickplay_question_widget.processor = processor
            self._quickplay_question_widget.load_new_question()
            self.stack.setCurrentWidget(self.quickplay_container)
            return

        processor = QuestionProcessor("Story", difficultyIndex=[0, 1])
        processor.process_file()

        def load_next_question():
            new_processor = QuestionProcessor("Story", difficultyIndex=[0, 1])
            new_processor.process_file()
            self._quickplay_question_widget.processor = new_processor
            self._quickplay_question_widget.load_new_question()

        self._quickplay_question_widget = QuestionWidget(processor, window=self, next_question_callback=load_next_question, tts=self.tts)
        self.quickplay_container.layout().addWidget(self._quickplay_question_widget)
        self.stack.setCurrentWidget(self.quickplay_container)
        apply_theme(self.quickplay_container, self.current_theme)

    def play_sound(self, filename):
        if self.is_muted:
            return
            
        # Cleanup old cache files
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
        
        # ✅ FIX RETAINED: Sync all audio buttons across the app
        icon_text = "🔇" if new_state else "🔊"
        accessible_name = "Audio Muted" if new_state else "Audio Unmuted"

        for btn in self.findChildren(QPushButton, "audio-button"):
            btn.setText(icon_text)
            btn.setAccessibleName(accessible_name)

        print("[AUDIO]", "Muted" if new_state else "Unmuted")
        
    def create_buttons(self):
        button_grid = QGridLayout() 
        button_grid.setSpacing(20) # More spacing for rich aesthetics
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
        buttons = ["Back to Operations", "Back to Home", "Settings"]
        translated = [tr(b) for b in buttons]

        callbacks = {
            tr("Back to Operations"): lambda: self.load_section("Operations"),
            tr("Back to Home"): self.back_to_home,
            tr("Settings"): self.handle_settings
        }

        footer = create_footer_buttons(translated, callbacks=callbacks)

        # ✅ FIX RETAINED: Audio button in section footer
        audio_btn = self.create_audio_button()
        footer.layout().insertWidget(0, audio_btn, alignment=Qt.AlignLeft)

        for btn in footer.findChildren(QPushButton):
            if btn.text() == tr("Back to Operations"):
                btn.setObjectName("back_to_operations")
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
            
            # ✅ FIX: Refresh the entire UI immediately if language changes
            if new_language != self.language:
                self.refresh_ui(new_language)

    def load_section(self, name):
        if hasattr(self, 'tts'):
            self.tts.stop()
        print(f"[INFO] Loading section: {name}")

        page = load_pages(name, self.back_to_main_menu,  difficulty_index=self.current_difficulty, main_window=self, tts=self.tts)

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
        
        upload_btn = self.main_footer.findChild(QPushButton, tr("Upload").lower().replace(" ", "_"))
        if upload_btn:
            upload_btn.show()
        
        back_btn = self.main_footer.findChild(QPushButton, tr("Back to Menu").lower().replace(" ", "_"))
        if back_btn:
            back_btn.hide()
        self.focus_quickplay_button()
        
    def back_to_home(self):
        # ✅ FIX RETAINED: "Back to Home" for Uploaded Quizzes goes to Mode Selection
        if isinstance(self.stack.currentWidget(), QuestionWidget):
            self.back_to_main_menu()
            return

        self.top_bar.show()  
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
        
        upload_btn = self.main_footer.findChild(QPushButton, tr("Upload").lower().replace(" ", "_"))
        if upload_btn:
            upload_btn.show()

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
        # Uniform scaling factoring based on both width and height
        width_scale = self.width() / 900.0 if self.width() > 0 else 1.0
        height_scale = self.height() / 600.0 if self.height() > 0 else 1.0
        scale = min(width_scale, height_scale)
        
        # Allow slight shrinking, e.g. down to 0.82 for smaller windows
        if scale < 0.82:
            scale = 0.82 
            
        footer_font_size = 17 * scale
        button_font_size = 18 * scale
        if getattr(self, 'language', '') == "മലയാളം":
            footer_font_size = 14 * scale # Shrink for Malayalam
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
        
        # Scale all menu buttons (including those in operations/subsections)
        for btn in self.findChildren(QPushButton):
            if not sip.isdeleted(btn) and btn.property("class") == "menu-button":
                max_width = int(340 * scale) if getattr(self, 'language', '') == "മലയാളം" else int(280 * scale)
                btn.setMaximumSize(max_width, int(75 * scale))
                
        # Scale active question widgets
        for qwidget in self.findChildren(QuestionWidget):
            if not sip.isdeleted(qwidget):
                qwidget.update_scaling(scale)
                    
        if hasattr(self, '_welcome_movie') and self._welcome_movie:
            if hasattr(self, 'gif_label') and self.gif_label:
                # Scale gif with window height, maintaining proportion
                target_size = int(280 * (self.height() / 600.0))
                target_size = min(max(200, target_size), 450)
                self._welcome_movie.setScaledSize(QSize(target_size, target_size))
                self.gif_label.setFixedSize(target_size, target_size)

        # Dynamic Footer heights supporting scaling avoids text clipping
        if hasattr(self, 'main_footer') and self.main_footer:
            self.main_footer.setMinimumHeight(int(65 * scale))
        if hasattr(self, 'section_footer') and self.section_footer:
            self.section_footer.setMinimumHeight(int(65 * scale))

        # Responsive Layout Switching for learn mode
        if hasattr(self, 'learn_mode_layout_box'):
            if self.width() < 950:
                self.learn_mode_layout_box.setDirection(QBoxLayout.TopToBottom)
            else:
                self.learn_mode_layout_box.setDirection(QBoxLayout.LeftToRight)
                
        # Scale learn_mode movie gif size
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