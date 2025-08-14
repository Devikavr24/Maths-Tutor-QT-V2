import sys, os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QDialog, QVBoxLayout,
    QPushButton, QComboBox, QHBoxLayout, QCheckBox, QFrame,
    QWidget, QGridLayout,QStackedWidget, QSizePolicy, QShortcut, QMessageBox
)
from PyQt5.QtCore import Qt,QUrl, QSize
from question.loader import QuestionProcessor
from pages.shared_ui import create_footer_buttons, apply_theme, SettingsDialog, create_main_footer_buttons
from pages.ques_functions import load_pages, upload_excel   # ← your new function

from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

from language.language import get_saved_language,save_selected_language_to_file,tr

from PyQt5.QtGui import QMovie, QKeySequence, QPixmap, QFont, QIcon






class RootWindow(QDialog):
    def __init__(self,minimal=False):
        super().__init__()
        self.minimal = minimal
        self.remember=False
        self.setWindowTitle("Maths Tutor - Language Selection Window")
        self.setFixedSize(400, 250 if not self.minimal else 150)
        self.init_ui()
        self.load_style("language_dialog.qss")
 
    def init_ui(self):
        layout = QVBoxLayout()

        if not self.minimal:
            title_label = QLabel("Welcome to Maths Tutor!")
            title_label.setProperty("class", "title")
            layout.addWidget(title_label)
            layout.addSpacing(15)
        language_label = QLabel("Select your preferred language:")
        language_label.setProperty("class", "subtitle")
 
        languages = ["English", "हिंदी", "മലയാളം", "தமிழ்", "عربي", "संस्कृत"]
        self.language_combo = QComboBox()
        self.language_combo.addItems(languages)
        self.language_combo.setProperty("class", "combo-box")
        layout.addWidget(language_label)
        layout.addWidget(self.language_combo)

        if not self.minimal:
            self.remember_check = QCheckBox("Remember my selection")
            self.remember_check.setChecked(False)
            self.remember_check.setProperty("class", "checkbox")
            layout.addWidget(self.remember_check)
        
        layout.addStretch()

        if not self.minimal:
            layout.addWidget(self.create_line())
        self.ok_button = QPushButton("Continue")
        self.ok_button.setDefault(True)
        self.ok_button.setAutoDefault(True)
        self.ok_button.setFocus()

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setAutoDefault(False)
        self.cancel_button.setShortcut(Qt.Key_Escape)
        self.cancel_button.setProperty("class", "danger-button") 


        btns = QHBoxLayout()
        btns.addStretch()
        btns.addWidget(self.cancel_button)
        btns.addWidget(self.ok_button)
        layout.addLayout(btns)
 
        self.setLayout(layout)
        self.cancel_button.clicked.connect(self.reject)
        self.ok_button.clicked.connect(self.handle_continue)



    


    def handle_continue(self):
        selected = self.language_combo.currentText()
        from language.language import set_language
        set_language(selected)
        print(selected)
        self.remember = self.remember_check.isChecked() if not self.minimal else False

        
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
        

        self.setWindowTitle("Maths Tutor")
        self.resize(900, 600)
        self.setMinimumSize(800, 550) 
        self.current_difficulty = 1  
        self.section_pages = {} 
        self.is_muted = False
        self.language = language

        from language import language
        language.selected_language=self.language
        self.init_ui()
        self.setup_shortcuts()

        self.load_style("main_window.qss")
        self.current_theme = "light"  # Initial theme


        self.media_player = QMediaPlayer()
        self.bg_player = QMediaPlayer()
        self.bg_player.setVolume(30)
        self.is_muted = False  # if not already present
        self.play_background_music()
        #self.player = self.setup_background_music()

        self.difficulty_index = 1 # Default to level 0 (e.g., "Very Easy")

    def init_ui(self):
        self.central_widget = QWidget()
        self.central_widget.setProperty("class", "central-widget")
        self.central_widget.setProperty("theme", "light")
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(4, 4, 4, 4)
        self.central_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.central_widget)

        self.current_theme = "light"

        # ✅ Global top bar with theme toggle button
        self.theme_button = QPushButton("🌙")
        self.theme_button.setToolTip("Toggle Light/Dark Theme")
        self.theme_button.clicked.connect(self.toggle_theme)
        self.theme_button.setAccessibleName("Theme Toggle Button")
        self.theme_button.setProperty("class", "menu-button")

        from language.language import translations
        desc = f"{translations[self.language]['welcome']} {translations[self.language]['ready'].format(lang=self.language)}"
        self.theme_button.setAccessibleDescription(desc)

        # ✅ Add theme button to global top bar
        self.top_bar = QWidget()
        self.top_bar_layout = QHBoxLayout(self.top_bar)
        self.top_bar_layout.setContentsMargins(0, 0, 0, 0)
        self.top_bar_layout.setSpacing(10)
        self.top_bar_layout.addWidget(self.theme_button, alignment=Qt.AlignLeft)
        self.top_bar_layout.addStretch()


        self.main_layout.addWidget(self.top_bar)  # ✅ Add top bar to top of layout

        # ✅ Menu page setup
        self.menu_widget = QWidget()
        menu_layout = QVBoxLayout()
        menu_layout.setSpacing(10)
        menu_layout.setAlignment(Qt.AlignTop)

        # Title and subtitle
        title = QLabel(tr("welcome"))
        title.setAlignment(Qt.AlignCenter)
        title.setProperty("class", "main-title")

        subtitle = QLabel(tr("ready").format(lang=self.language))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setProperty("class", "subtitle")

        menu_layout.addWidget(title)
        menu_layout.addWidget(subtitle)
        menu_layout.addSpacing(20)

        # Section buttons
        menu_layout.addLayout(self.create_buttons())
        menu_layout.addSpacing(10)
        menu_layout.addStretch()

        # GIF Section 
        self.gif_label = QLabel()
        self.gif_label.setAlignment(Qt.AlignCenter)
        self.movie = QMovie("images/welcome-1.gif")
        self.movie.setScaledSize(QSize(150, 150))
        self.gif_label.setMovie(self.movie)
        self.movie.start()

        gif_container = QWidget()
        gif_layout = QHBoxLayout()
        gif_layout.setContentsMargins(0, 0, 0, 0)
        gif_layout.addStretch()
        gif_layout.addWidget(self.gif_label, alignment=Qt.AlignCenter)
        gif_layout.addStretch()
        gif_container.setLayout(gif_layout)

        menu_layout.addWidget(gif_container)
        self.menu_widget.setLayout(menu_layout)

        # Stack and footers
        self.stack = QStackedWidget()
        self.stack.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Create the mode selection page (startup)
        self.startup_widget = self.create_mode_selection_page()
        self.stack.addWidget(self.startup_widget)  # index 0

    # Create the home menu page
        
        self.stack.addWidget(self.menu_widget)     # index 1

# Show the startup (mode selection) page first
        self.stack.setCurrentWidget(self.startup_widget)

# Add the stacked widget to main layout
        self.main_layout.addWidget(self.stack)

# Create the footers
        self.main_footer = create_main_footer_buttons(self)   # For startup & home
        self.section_footer = self.create_section_footer()     # For sections only

# Footer style & height
        for footer in (self.main_footer, self.section_footer):
            footer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            footer.setMinimumHeight(63)

    # Add both footers to layout
        self.main_layout.addWidget(self.main_footer)
        self.main_layout.addWidget(self.section_footer)

        # Show main footer initially, hide section footer
    
        self.section_footer.hide()


        apply_theme(self.central_widget, self.current_theme)

            
        # ✅ Always ensure Story button gets focus on UI load
        self.focus_story_button()

    def focus_story_button(self):
        """✅ Ensure Story button is focused (called on init and return)"""
        for btn in self.menu_buttons:
            if btn.text() == tr("Story"):
                btn.setFocus()
                break

    def create_mode_selection_page(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        widget.setLayout(layout)

        label = QLabel("Choose Mode")
        label.setAlignment(Qt.AlignCenter)
        label.setProperty("class", "main-title")
        layout.addWidget(label)

        buttons = [
             ("⚡ Quickplay", self.start_quickplay_mode),
            ("🎮 Game Mode", self.start_game_mode),
            ("🎓 Learning Mode", self.start_learning_mode)
        ]

        for text, callback in buttons:
            btn = QPushButton(text)
            btn.setMinimumSize(240, 65)  # ✅ Uniform large size for all mode buttons
            btn.setProperty("class", "menu-button")  # ✅ Set QSS class for each button
            btn.setProperty("theme", self.current_theme)
            btn.clicked.connect(callback)
            layout.addWidget(btn)
            
        if text.startswith("⚡ Quickplay"):
            btn.setFocus()        # Highlight it
            btn.setDefault(True)  # Enter/Return triggers it

        
        

        return widget

    def start_learning_mode(self):
        self.stack.setCurrentWidget(self.menu_widget)
        self.main_footer.show()
        self.section_footer.hide()
        self.play_sound("click-button.wav")

    def start_game_mode(self):
        self.clear_main_layout()

        widget = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        widget.setLayout(layout)

    # Title
        title_label = QLabel("Select Game Difficulty")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setProperty("class", "main-title")  # Styled in QSS
        layout.addWidget(title_label)

    # Subtitle
        subtitle_label = QLabel("Choose your challenge level")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setProperty("class", "subtitle")  # Optional: define in QSS
        layout.addWidget(subtitle_label)

    # Difficulty Buttons (Blue Theme, Large, Rounded)
        difficulties = [
            (" Easy", 1),
            (" Medium", 2),
            (" Hard", 3),
            (" Extra Hard", 4)
        ]
        for text, index in difficulties:
            btn = QPushButton(text)
            btn.setMinimumSize(260, 70)  # Large size
            btn.setProperty("class", "menu-button")  # Uses your blue theme QSS
            btn.setProperty("theme", self.current_theme)
            btn.clicked.connect(lambda _, idx=index: self.load_game_questions(idx))
            layout.addWidget(btn)

    # Mole Image (optional visual match to menu)
        mole_label = QLabel()
        mole_label.setPixmap(QPixmap("assets/mole.png").scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        mole_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(mole_label)

   

        self.main_layout.addWidget(widget)

    def load_game_questions(self, difficulty_index):
        from pages.shared_ui import QuestionWidget
        from question.loader import QuestionProcessor
        import random

        self.clear_main_layout()

        self.game_types = ["Multiplication", "Percentage", "Division", "Currency", "Story", "Time", "Distance", "Bellring","Addition", "Subtraction", "Remainder"]
        self.game_difficulty = difficulty_index

        def load_next_question():
            random_type = random.choice(self.game_types)
            print("[load_game_question] current random type:", random_type)
            processor = QuestionProcessor(random_type, difficultyIndex=[self.game_difficulty])
            processor.process_file()
            question_widget = QuestionWidget(processor, window=self, next_question_callback=load_next_question)
            self.clear_main_layout()
            self.main_layout.addWidget(question_widget)

        load_next_question()



    def start_quickplay_mode(self):
        from pages.shared_ui import QuestionWidget
        from question.loader import QuestionProcessor

        processor = QuestionProcessor("Story", difficultyIndex=[0, 1])  # Easy + Medium
        processor.process_file()

        self.clear_main_layout()
        question_widget = QuestionWidget(processor, window=self)
        self.main_layout.addWidget(question_widget)
        
        footer = create_footer_buttons(
        ["Back to Menu"],
        callbacks={"Back to Menu": self.create_mode_selection_page}
        )

        
        audio_btn = self.create_audio_button()
        footer.layout().insertWidget(0, audio_btn)

        self.main_layout.addWidget(footer)
        
        
















    def play_sound(self, filename):
        
        if self.is_muted:
            print("[SOUND] Muted, not playing:", filename)
            return
        
        filepath = os.path.abspath(os.path.join("sounds", filename))
        if os.path.exists(filepath):
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(filepath)))
            self.media_player.play()
        else:
            print(f"[SOUND ERROR] File not found: {filepath}")
    def play_background_music(self):
        if self.is_muted:
            print("[BG MUSIC] Muted.")
            return

        filepath = os.path.abspath(os.path.join("sounds", "backgroundmusic.mp3"))
        if os.path.exists(filepath):
            self.bg_player.setMedia(QMediaContent(QUrl.fromLocalFile(filepath)))
            self.bg_player.setVolume(30)
            self.bg_player.play()
            self.bg_player.mediaStatusChanged.connect(self.loop_background_music)
            print("[BG MUSIC] Playing background music.")
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
        # ✅ Make sure it can receive focus by Tab
        self.audio_button.setFocusPolicy(Qt.StrongFocus)
        return self.audio_button

    def set_mute(self, state: bool):
        self.is_muted = state
        if hasattr(self, 'bg_player') and self.bg_player is not None:
            if state:
                self.bg_player.pause()  # or .stop() if you want to fully stop it
                print("[BG MUSIC] Paused due to mute.")
            else:
                self.play_background_music()
    def toggle_audio(self):
        new_state = not self.is_muted
        self.set_mute(new_state)
        self.audio_button.setText("🔇" if new_state else "🔊")
        print("[AUDIO]", "Muted" if new_state else "Unmuted")
        

      
    def create_buttons(self):
        button_grid = QGridLayout()
        button_grid.setSpacing(12)
        button_grid.setContentsMargins(6, 6, 6, 6)

        sections = ["Story", "Time", "Currency", "Distance", "Bellring", "Operations"]
        self.menu_buttons = []

        # Add 6 section buttons in 2 rows
        for i, name in enumerate(sections):
            translated_name = tr(name)
            button = QPushButton(translated_name)
            button.setMinimumSize(160, 45)
            button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
            button.setProperty("class", "menu-button")
            button.setAccessibleName(translated_name)
            button.clicked.connect(lambda checked, n=name: self.load_section(n))

            self.menu_buttons.append(button)
            row, col = divmod(i, 3)
            button_grid.addWidget(button, row, col)

        # 🔁 Calculate next available row dynamically
        next_row = (len(sections) + 2) // 3

        

        return button_grid
    
    


    

    def create_section_footer(self):
        buttons = ["Back to Operations", "Back to Home", "Settings"]
        translated = [tr(b) for b in buttons]

        # Create a mapping from translated labels to callbacks
        callbacks = {
            tr("Back to Operations"): lambda: self.load_section("Operations"),
            tr("Back to Home"): self.back_to_home,
            tr("Settings"): self.handle_settings
        }

        # Create the footer with translated labels and callbacks
        footer = create_footer_buttons(translated, callbacks=callbacks)

        # ✅ Assign objectName for visibility toggling (very important!)
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
            # Update global difficulty and language
            self.current_difficulty = dialog.get_difficulty_index()
            self.language = dialog.get_selected_language()

            self.setWindowTitle(f"Maths Tutor - {self.language}")

            # Reload current section if not on main menu
            current_widget = self.stack.currentWidget()
            if current_widget != self.menu_widget:
                for section_name, page in self.section_pages.items():
                    if page == current_widget:
                        self.section_pages.pop(section_name)
                        new_page = load_pages(
                            section_name,
                            back_callback=self.back_to_main_menu,
                            difficulty_index=self.current_difficulty,
                            main_window=self
                        )
                        self.section_pages[section_name] = new_page
                        self.stack.addWidget(new_page)
                        self.stack.setCurrentWidget(new_page)
                        break

    def load_section(self, name):
        print(f"[INFO] Loading section: {name}")

        if not hasattr(self, 'section_pages'):
            self.section_pages = {}

        if name not in self.section_pages:
            # Always call load_pages to load/reload based on current difficulty
            page = load_pages(name,self.back_to_main_menu,  difficulty_index=self.current_difficulty, main_window=self)

            if hasattr(self, "current_theme"):
                page.style().unpolish(page)
                page.style().polish(page)
                apply_theme(page, self.current_theme)  # ✅ Apply current theme
            self.section_pages[name] = page
            self.stack.addWidget(page)

        self.stack.setCurrentWidget(self.section_pages[name])
        self.menu_widget.hide()
        self.main_footer.hide()
        self.section_footer.show()
        self.update_back_to_operations_visibility(name)
    
    def back_to_main_menu(self):
        """Switch to the mode selection (startup) page."""
        self.play_sound("home_button_sound.wav")
        self.stack.setCurrentWidget(self.startup_widget)  # ✅ Show mode selection page
        self.section_footer.hide()
        self.main_footer.show()
    def back_to_home(self):
        """Switch to the home menu page."""
        self.stack.setCurrentWidget(self.menu_widget)     # ✅ Show home menu page
        self.section_footer.hide()                        # ✅ Hide section footer
        self.main_footer.show()                           # ✅ Show main footer


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
                self.setStyleSheet(f.read())

    def toggle_theme(self):
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        print("Theme switched to:", self.current_theme)
        self.theme_button.setText("☀️" if self.current_theme == "dark" else "🌙")
        apply_theme(self.central_widget, self.current_theme)
        #self.tts.speak(f"{self.current_theme.capitalize()} theme activated")
    
    def setup_shortcuts(self):  # ✅ Newly added method
        exit_shortcut = QShortcut(QKeySequence("Ctrl+Q"), self)
        exit_shortcut.setContext(Qt.ApplicationShortcut)
        exit_shortcut.activated.connect(self.confirm_exit)

    def confirm_exit(self):
        reply = QMessageBox.question(
            self,
            "Exit Application",
            "Are you sure you want to exit?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            QApplication.quit()

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self,
            "Exit Application",
            "Are you sure you want to exit?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def update_back_to_operations_visibility(self, section_name):
        operation_subsections = {
            "addition", "subtraction", "multiplication",
            "division", "remainder", "percentage"
        }
        normalized = section_name.strip().lower()
        # Find the button by objectName (assigned in shared_ui)
        back_to_ops_btn = self.section_footer.findChild(QPushButton, "back_to_operations")
        if back_to_ops_btn:
            back_to_ops_btn.setVisible(normalized in operation_subsections)
    

if __name__ == "__main__":

    app = QApplication(sys.argv)
    style_file = os.path.join("styles", "app.qss")
    if os.path.exists(style_file):
        with open(style_file, "r") as f:
            app.setStyleSheet(f.read())
 

    
    lang=get_saved_language()
    if lang:
        print(lang)
        window = MainWindow(language=lang)
        window.show()
        sys.exit(app.exec_())
    else:
        dialog = RootWindow()
        if dialog.exec_() == QDialog.Accepted:
            window = MainWindow(language=dialog.language_combo.currentText())
            window.show()
            sys.exit(app.exec_())