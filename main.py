import sys, os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QDialog, QVBoxLayout,
    QPushButton, QComboBox, QHBoxLayout, QCheckBox, QFrame,
    QWidget, QGridLayout,QStackedWidget, QSizePolicy
)
from PyQt5.QtCore import Qt
from question.loader import QuestionProcessor
from pages.shared_ui import create_footer_buttons, SettingsDialog
from pages.ques_functions import load_pages, upload_excel  # ← your new function
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl



from language import language 
from language.language import tr



class RootWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Maths Tutor - Language Selection")
        self.setFixedSize(400, 250)
        self.init_ui()
        self.load_style("language_dialog.qss")
 
    def init_ui(self):
        title_label = QLabel("Welcome to Maths Tutor!")
        title_label.setProperty("class", "title")
 
        language_label = QLabel("Select your preferred language:")
        language_label.setProperty("class", "subtitle")
 
        languages = ["English", "हिंदी", "മലയാളം", "தமிழ்", "عربي", "संस्कृत"]
        self.language_combo = QComboBox()
        self.language_combo.addItems(languages)
        self.language_combo.setProperty("class", "combo-box")
        


        self.remember_check = QCheckBox("Remember my selection")
        self.remember_check.setChecked(False)


        self.ok_button = QPushButton("Continue")
        self.ok_button.setDefault(True)
        self.ok_button.setAutoDefault(True)
        self.ok_button.setFocus()

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setAutoDefault(False)
        self.cancel_button.setShortcut(Qt.Key_Escape)


       

        layout = QVBoxLayout()
        layout.addWidget(title_label)
        layout.addSpacing(15)
        layout.addWidget(language_label)
        layout.addWidget(self.language_combo)
        layout.addWidget(self.remember_check)
        layout.addStretch()
        layout.addWidget(self.create_line())
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
        language.selected_language = selected  # ✅ Now this will work
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
        self.setWindowTitle(f"Maths Tutor - {language}")
        self.resize(900, 600)
        self.setMinimumSize(800, 550) 
        self.current_difficulty = 1  
        self.section_pages = {} 
        self.is_muted = False
        self.language = language
        self.init_ui()
        self.load_style("main_window.qss")
        self.current_theme = "light"  # Initial theme
        self.media_player = QMediaPlayer()
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

        # Track current theme
        self.current_theme = "light"
        
        self.menu_widget = QWidget()
        menu_layout = QVBoxLayout()
        menu_layout.setAlignment(Qt.AlignCenter)
    
         # Top bar for theme toggle
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(0, 0, 0, 0)

         # Theme button (🌙 for light, ☀️ for dark)
        self.theme_button = QPushButton("🌙")
        self.theme_button.setFixedSize(40, 40)
        self.theme_button.setToolTip("Toggle Light/Dark Theme")
        self.theme_button.clicked.connect(self.toggle_theme)

        top_bar.addWidget(self.theme_button, alignment=Qt.AlignLeft)
        top_bar.addStretch()

        menu_layout.addLayout(top_bar)

        
        title = QLabel(tr("welcome")) #welcome to maths tutor 


        title.setAlignment(Qt.AlignCenter)
        title.setProperty("class", "main-title")
 
        subtitle = QLabel(tr("ready").format(lang=self.language))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setProperty("class", "subtitle")
 
        menu_layout.addWidget(title)
        menu_layout.addWidget(subtitle)
        menu_layout.addSpacing(20)

        menu_layout.addLayout(self.create_buttons())
        menu_layout.addStretch()
        # Bottom-left audio toggle
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 0, 0, 0)

        self.audio_button = QPushButton("🔊")
        self.audio_button.setObjectName("audio-button")
        self.audio_button.setFixedSize(50, 50)
        self.audio_button.setToolTip("Toggle Mute/Unmute")
        self.audio_button.clicked.connect(self.toggle_audio)

        bottom_layout.addWidget(self.audio_button, alignment=Qt.AlignLeft)
        bottom_layout.addStretch()

        menu_layout.addLayout(bottom_layout)

        self.menu_widget.setLayout(menu_layout)

        self.stack = QStackedWidget()
        self.stack.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.stack.addWidget(self.menu_widget)

        self.main_layout.addWidget(self.stack)
        self.main_footer = self.create_main_footer_buttons()
        self.section_footer = self.create_section_footer()
        self.main_layout.addWidget(self.main_footer)
        self.main_layout.addWidget(self.section_footer)
        self.section_footer.hide()
    
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

    def set_mute(self, state: bool):
        self.is_muted = state

    def toggle_audio(self):
        new_state = not self.is_muted
        self.set_mute(new_state)
        self.audio_button.setText("🔇" if new_state else "🔊")


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
            button.setMaximumSize(220, 60)  # Optional: Prevent growing too big

             # Use Preferred policy to allow controlled resizing
            button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

            button.setProperty("class", "menu-button")
            button.clicked.connect(lambda checked, n=name: self.load_section(n))

            self.menu_buttons.append(button)
            row, col = divmod(i, 3)
            button_grid.addWidget(button, row, col)

            
        return button_grid 

    def create_main_footer_buttons(self):
        buttons = ["Upload", "Help", "About", "Settings"]
        translated = [tr(b) for b in buttons]
        return create_footer_buttons(
            translated,
            callbacks={
                "Upload": self.handle_upload,
                "Settings": self.handle_settings
        }
    )

    def create_section_footer(self):
        buttons=["Help", "About", "Settings"]
        translated=[tr(b) for b in buttons]
        return create_footer_buttons(
            translated,
            callbacks={
                "Settings": self.handle_settings
            }
        )

    def handle_settings(self):
        

        dialog = SettingsDialog(
            parent=self,
            initial_difficulty=getattr(self, "current_difficulty", 1)
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
                page.setProperty("theme", self.current_theme)
                page.style().unpolish(page)
                page.style().polish(page)

            self.section_pages[name] = page
            self.stack.addWidget(page)

        self.stack.setCurrentWidget(self.section_pages[name])
        self.menu_widget.hide()
        self.main_footer.hide()
        self.section_footer.show()

    def back_to_main_menu(self):
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
        self.central_widget.setProperty("theme", self.current_theme)
        self.central_widget.style().unpolish(self.central_widget)
        self.central_widget.style().polish(self.central_widget)
        self.theme_button.setText("☀️" if self.current_theme == "dark" else "🌙")


if __name__ == "__main__":

    app = QApplication(sys.argv)
    style_file = os.path.join("styles", "app.qss")
    if os.path.exists(style_file):
        with open(style_file, "r") as f:
            app.setStyleSheet(f.read())
 
    dialog = RootWindow()
    if dialog.exec_() == QDialog.Accepted:
        window = MainWindow(language=dialog.language_combo.currentText())
        window.show()
        sys.exit(app.exec_())