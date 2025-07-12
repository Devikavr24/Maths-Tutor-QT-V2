import sys, os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QDialog, QVBoxLayout,
    QPushButton, QComboBox, QHBoxLayout, QCheckBox, QFrame,
    QWidget, QGridLayout,QStackedWidget, QSizePolicy, QShortcut, QMessageBox
)
from PyQt5.QtCore import Qt
from question.loader import QuestionProcessor
from pages.shared_ui import create_footer_buttons, apply_theme, SettingsDialog
from pages.ques_functions import load_pages, upload_excel   # ← your new function

from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl

from language.language import get_saved_language,save_selected_language_to_file,tr

from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import QSize

from PyQt5.QtGui import QKeySequence





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
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.central_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.central_widget)

        self.current_theme = "light"  # Initial theme

        # Menu page content
        self.menu_widget = QWidget()
        menu_layout = QVBoxLayout()
        menu_layout.setAlignment(Qt.AlignTop)

        # Top bar with theme toggle
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(0, 0, 0, 0)

        self.theme_button = QPushButton("🌙")
        self.theme_button.setToolTip("Toggle Light/Dark Theme")
        self.theme_button.clicked.connect(self.toggle_theme)
        self.theme_button.setAccessibleName("Theme Toggle Button")
        self.theme_button.setProperty("class", "menu-button")

        from language.language import translations
        desc = f"{translations[self.language]['welcome']} {translations[self.language]['ready'].format(lang=self.language)}"
        self.theme_button.setAccessibleDescription(desc)

        top_bar.addWidget(self.theme_button, alignment=Qt.AlignLeft)
        top_bar.addStretch()
        menu_layout.addLayout(top_bar)

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

       # GIF Section 
        self.gif_label = QLabel()
        self.gif_label.setAlignment(Qt.AlignCenter)
        self.movie = QMovie("images/welcome-1.gif")
        self.movie.setScaledSize(QSize(200, 200))
        self.gif_label.setMovie(self.movie)
        self.movie.start()

        gif_container = QWidget()
        gif_container.setFixedHeight(220)
        gif_layout = QHBoxLayout()
        gif_layout.setContentsMargins(0, 0, 0, 0)
        gif_layout.addStretch()
        gif_layout.addWidget(self.gif_label, alignment=Qt.AlignCenter)
        gif_layout.addStretch()
        gif_container.setLayout(gif_layout)

        menu_layout.addWidget(gif_container)

        # Bottom audio toggle
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        self.audio_button = QPushButton("🔊")
        self.audio_button.setObjectName("audio-button")
        self.audio_button.setToolTip("Toggle Mute/Unmute")
        self.audio_button.clicked.connect(self.toggle_audio)
        bottom_layout.addWidget(self.audio_button, alignment=Qt.AlignLeft)
        bottom_layout.addStretch()
        menu_layout.addLayout(bottom_layout)

        self.menu_widget.setLayout(menu_layout)

        # Stack and footers
        self.stack = QStackedWidget()
        self.stack.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.stack.addWidget(self.menu_widget)
        self.main_layout.addWidget(self.stack)

        self.main_footer = self.create_main_footer_buttons()
        self.section_footer = self.create_section_footer()
        for footer in [self.main_footer, self.section_footer]:
            footer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            footer.setMinimumHeight(63)

        self.main_layout.addWidget(self.main_footer)
        self.main_layout.addWidget(self.section_footer)
        self.section_footer.hide()

        apply_theme(self.central_widget, self.current_theme)


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
        button_grid.setSpacing(10)
        button_grid.setContentsMargins(10, 10, 10, 10)

        sections = ["Story", "Time", "Currency", "Distance", "Bellring", "Operations"]
        self.menu_buttons = []

        for i, name in enumerate(sections):
            translated_name = tr(name)
            button = QPushButton(translated_name)

            # Set a good preferred base size
            button.setMinimumSize(160, 50)
            button.setMaximumSize(220, 60)
            button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
            button.setProperty("class", "menu-button")

            # Set accessible name for all buttons
            button.setAccessibleName(translated_name)

            button.clicked.connect(lambda checked, n=name: self.load_section(n))

            self.menu_buttons.append(button)
            row, col = divmod(i, 3)
            button_grid.addWidget(button, row, col)

        return button_grid


    def create_main_footer_buttons(self):
        buttons = ["Upload", "Help", "About", "Settings"]
        translated = {tr(b): b for b in buttons}  
       
        return create_footer_buttons(
            list(translated.keys()),
            callbacks={
                "Upload": self.handle_upload,
                tr("Settings"): self.handle_settings
        }
    )

    

    def create_section_footer(self):
        buttons = ["Back to Operations", "Back to Home", "Help", "About", "Settings"]
        translated = [tr(b) for b in buttons]

        # Create a mapping from translated labels to callbacks
        callbacks = {
            tr("Back to Operations"): lambda: self.load_section("Operations"),
            tr("Back to Home"): self.back_to_main_menu,
            tr("Help"): self.show_help if hasattr(self, "show_help") else lambda: None,
            tr("About"): self.show_about if hasattr(self, "show_about") else lambda: None,
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
            page = load_pages(name, self.back_to_main_menu, difficulty_index=self.current_difficulty, main_window=self)

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
        self.play_sound("home_button_sound.wav")  
        self.stack.setCurrentWidget(self.menu_widget)
        self.menu_widget.show()
        self.section_footer.hide()
        self.main_footer.show()

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
        widgets_to_update = [
            self.central_widget,
            self.menu_widget,
            self.main_footer,
            self.section_footer
        ] + list(self.section_pages.values())

        for widget in widgets_to_update:
            apply_theme(widget, self.current_theme)
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