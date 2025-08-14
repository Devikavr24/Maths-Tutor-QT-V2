# pages/shared_ui.py

from PyQt5.QtWidgets import ( QWidget, QLabel, QHBoxLayout, QPushButton,
                              QVBoxLayout,QSizePolicy, QDialog, QSlider, QDialogButtonBox
                              ,QSpacerItem,QLineEdit,QMessageBox)

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QPalette, QColor, QIntValidator
from question.loader import QuestionProcessor
from time import time
import random 
from tts.tts_worker import TextToSpeech


DIFFICULTY_LEVELS = ["Simple", "Easy", "Medium", "Hard", "Challenging"]

from language.language import set_language,clear_remember_language,tr

from language.language import tr
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtGui import QMovie

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QTimer

def create_entry_ui(main_window) -> QWidget:
    entry_widget = QWidget()
    entry_widget.setProperty("theme", main_window.current_theme) 
    layout = QVBoxLayout()
    layout.setAlignment(Qt.AlignCenter)

    label = QLabel("Click below to start the quiz")
    label.setFont(QFont("Arial", 24))
    label.setAlignment(Qt.AlignCenter)

    def start_quiz():
        print("Start button clicked")  # ✅ DEBUG POINT
        from pages.ques_functions import start_uploaded_quiz
        start_uploaded_quiz(main_window)
    
    button = create_menu_button("Start", start_quiz)
    button.clicked.connect(start_quiz)

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
    button.setFixedSize(200, 40)
    button.setProperty("class", "menu-button")
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
    input_box.setFixedSize(width, height)
    input_box.setAlignment(Qt.AlignCenter)
    input_box.setPlaceholderText(tr("Enter your answer"))
    input_box.setFont(QFont("Arial", font_size))
    input_box.setValidator(QIntValidator(0, 1000000))  # only positive integers
    input_box.setProperty("class", "answer-input")
    return input_box

def wrap_center(widget):
    container = QWidget()
    layout = QHBoxLayout()
    layout.addStretch()             # Push from the left
    layout.addWidget(widget)        # The centered widget
    layout.addStretch()             # Push from the right
    container.setLayout(layout)
    return container

class QuestionWidget(QWidget):
    def __init__(self, processor,window=None,next_question_callback=None):
        super().__init__()
        self.processor = processor
        self.answer = None
        self.start_time = time()
        self.next_question_callback = next_question_callback
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)
        self.main_window = window
        self.setProperty("theme", window.current_theme)
        self.tts = TextToSpeech() # your TTS instance
        self.init_ui()
       
    def init_ui(self):
        self.question_area = QWidget()
        question_layout = QVBoxLayout()
        question_layout.setAlignment(Qt.AlignCenter)
        self.question_area.setLayout(question_layout)

        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setProperty("class", "question-label")
        self.label.setWordWrap(True)
       
        question_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        question_layout.addWidget(self.label)
        question_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # ✅ Styled input box (your own function)
        self.input_box = create_answer_input()
        self.input_box.returnPressed.connect(self.check_answer)

        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignCenter)
        
        self.result_label.setFont(QFont("Arial", 46))

        #🧱 Assemble the main layout
        self.layout.addWidget(self.question_area)
        self.layout.addSpacing(20)
        self.layout.addWidget(self.input_box, alignment=Qt.AlignCenter)
        self.layout.addSpacing(10)
        self.layout.addWidget(self.result_label)
        self.layout.addStretch()

        self.gif_feedback_label = QLabel()
        self.gif_feedback_label.setVisible(False)  # Hidden by default
        self.processor.widget = self
        # Make sure your widget has a layout
        #layout = self.layout
        #if layout is None:
         #   layout = QVBoxLayout()
          #  self.setLayout(layout)

        #layout.addWidget(self.gif_feedback_label, alignment=Qt.AlignCenter)
        self.gif_feedback_label = QLabel()
        self.gif_feedback_label.setVisible(False)
        self.gif_feedback_label.setAlignment(Qt.AlignCenter)
        self.gif_feedback_label.setScaledContents(True)
        self.gif_feedback_label.setMinimumSize(300, 300)
        self.gif_feedback_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        

        # Add the GIF label to your layout (ideally after the question/answer widgets)
        self.layout.addWidget(self.gif_feedback_label, alignment=Qt.AlignCenter)



        self.load_new_question()
        
    def show_feedback_gif(self, sound_filename):
        
        if sound_filename == "question":
            print("[GIF] Question gif")
            gif_name = f"question-{random.choice([1, 2])}.gif"
        else:  
            gif_name = sound_filename.replace(".mp3", ".gif")
        gif_path = f"images/{gif_name}"

        movie = QMovie(gif_path)

        # Set a fixed size to scale the gif
        movie.setScaledSize(QSize(200, 200))  # Adjust this as needed

        self.gif_feedback_label.setFixedSize(200, 200)
        self.gif_feedback_label.setAlignment(Qt.AlignCenter)
        self.gif_feedback_label.setMovie(movie)
        self.gif_feedback_label.setVisible(True)
        movie.start()


            
    def hide_feedback_gif(self):
        self.gif_feedback_label.setVisible(False)
        self.gif_feedback_label.clear()

    def end_session(self):
        #if hasattr(self, 'bg_player') and self.bg_player is not None:
    
        self.main_window.bg_player.stop()   
        print("[BG MUSIC] Stopped due to end session.")
        if self.main_window:
            from main import MainWindow  # Import your section menu window
            self.main_window.back_to_main_menu()



    
    def load_new_question(self):
        if hasattr(self, "gif_feedback_label"):
    
            self.hide_feedback_gif()

        
        question_text, self.answer = self.processor.get_questions()
        self.start_time = time()
        self.label.setText(question_text)
        
        self.input_box.setText("")  # ✨ Clear only the input
        self.result_label.setText("")
        self.show_feedback_gif("question")


        # Speak question for accessibility
        if hasattr(self, 'tts'):
            self.tts.speak(question_text)

    
            
    def check_answer(self):
        try:
            user_input = self.input_box.text().strip()
            user_answer = float(user_input)
            elapsed = time() - self.start_time

            correct = float(user_answer) == float(self.answer)
            self.processor.submit_answer(user_answer, self.answer, elapsed)

            if correct:
                #self.result_label.setMinimumHeight(200)
                self.result_label.setText('<span style="font-size:16pt;">Correct!</span>')



               
                sound_index = random.randint(1, 3)
                
                if elapsed < 5:
                    feedback_text = "🌟 Excellent"
                    if self.main_window and callable(getattr(self.main_window, "play_sound", None)):
                        sound_file = f"excellent-{sound_index}.mp3"
                        
                elif elapsed < 10:
                    if self.main_window:
                        feedback_text = "👏 Very Good"
                        sound_file =f"very-good-{sound_index}.mp3"
                elif elapsed < 15:
                    if self.main_window:
                        feedback_text = "👍 Good"
                        sound_file =f"good-{sound_index}.mp3"
                elif elapsed < 20:
                    if self.main_window:
                        feedback_text = "👌 Not Bad"
                        sound_file =f"not-bad-{sound_index}.mp3"
                else:
                    if self.main_window:
                        feedback_text = "🙂 Okay"
                        sound_file =f"okay-{sound_index}.mp3"

                self.result_label.setText(f'<span style="font-size:16pt;">{feedback_text}</span>')
                self.main_window.play_sound(sound_file)
                self.show_feedback_gif(sound_file)
                  # ✅ Show the GIF
                self.processor.retry_count = 0

                #
                # QTimer.singleShot(2000, lambda: self.show_feedback_gif("question-1.mp3"))
                QTimer.singleShot(2000, self.call_next_question)


            else:
                self.processor.retry_count += 1
                sound_index = random.randint(1, 2)
                if self.processor.retry_count == 1:
                    sound_file = f"wrong-anwser-{sound_index}.mp3"
                else:
                    sound_file = f"wrong-anwser-repeted-{sound_index}.mp3"

                self.main_window.play_sound(sound_file)
                self.show_feedback_gif(sound_file)

                
                self.result_label.setText('<span style="font-size:16pt;">Try Again.</span>')
               


        except Exception as e:
            self.result_label.setText(f"Error: {str(e)}")

    def call_next_question(self):
        if hasattr(self, "next_question_callback") and self.next_question_callback:
            self.next_question_callback()
        else:
            self.load_new_question()



def create_dynamic_question_ui(section_name, difficulty_index, back_callback,main_window=None, back_to_operations_callback=None):
    container = QWidget()
    layout = QVBoxLayout()
    layout.setAlignment(Qt.AlignTop)
    container.setLayout(layout)

    processor = QuestionProcessor(section_name, difficulty_index)
    processor.process_file()
    
    question_widget = QuestionWidget(processor,main_window)

    layout.addWidget(question_widget)
    apply_theme(container, main_window.current_theme)
    return container


def apply_theme(widget, theme):
    if not widget:
        return

    widget.setProperty("theme", theme)
    widget.setStyleSheet("")
    widget.style().unpolish(widget)
    widget.style().polish(widget)

    for child in widget.findChildren((QWidget, QLabel, QLineEdit, QPushButton)):
        child.setProperty("theme", theme)
        child.setStyleSheet("")
        child.style().unpolish(child)
        child.style().polish(child)

class SettingsDialog(QDialog):
    def __init__(self, parent=None, initial_difficulty=1, main_window=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setFixedSize(400, 220)

        self.main_window = main_window
        self.updated_language = main_window.language if main_window else "English"

        self.tts = TextToSpeech()  # TTS instance

        self.difficulty_slider = QSlider(Qt.Horizontal)
        self.difficulty_slider.setMinimum(0)
        self.difficulty_slider.setMaximum(len(DIFFICULTY_LEVELS) - 1)
        self.difficulty_slider.setSingleStep(1)
        self.difficulty_slider.setPageStep(1)
        self.difficulty_slider.setTickInterval(1)
        self.difficulty_slider.setTickPosition(QSlider.TicksBelow)
        self.difficulty_slider.setTracking(True)
        self.difficulty_slider.setFocusPolicy(Qt.StrongFocus)
        self.difficulty_slider.setFocus()
        self.difficulty_slider.setAccessibleName("Difficulty slider")
        self.difficulty_slider.setAccessibleDescription(f"Use left or right arrow keys to select difficulty level. The levels are Simple, Easy, Medium, Hard and challenging.")
        self.difficulty_slider.setValue(initial_difficulty)
        self.difficulty_label = create_label(DIFFICULTY_LEVELS[initial_difficulty], font_size=12)
       
        self.difficulty_slider.valueChanged.connect(self.update_difficulty_label)
        

    

        # 🔁 Reset Language Button
        self.language_reset_btn = QPushButton("Reset Language")
        self.language_reset_btn.setFixedHeight(30)
        self.language_reset_btn.clicked.connect(self.handle_reset_language)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept_settings)
        button_box.rejected.connect(self.reject)

        self.setMinimumSize(400, 280)  # Better size for spacing

        layout = QVBoxLayout()
        layout.setSpacing(12)  # Add breathing space between widgets
        layout.setContentsMargins(20, 20, 20, 20)

        layout.addWidget(create_label("Select Difficulty:", font_size=12, bold=False))
        layout.addWidget(self.difficulty_slider)
        layout.addWidget(self.difficulty_label)

        layout.addWidget(self.language_reset_btn)

        # Add Help and About side by side
        extra_buttons_layout = QHBoxLayout()
        self.help_button = QPushButton("Help")
        self.about_button = QPushButton("About")
        for btn in [self.help_button, self.about_button]:
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            btn.setFixedHeight(30)
        extra_buttons_layout.addWidget(self.help_button)
        extra_buttons_layout.addWidget(self.about_button)
        layout.addLayout(extra_buttons_layout)

        layout.addStretch()
        layout.addWidget(button_box)

        self.setLayout(layout)


    def update_difficulty_label(self, index):
        level = DIFFICULTY_LEVELS[index]
        self.difficulty_label.setText(level)

    # For screen reader
        self.difficulty_slider.setAccessibleDescription(
            f"Difficulty level selected: {level}. Use left or right arrow keys to change it. "
            "Levels are: Simple, Easy, Medium, Hard, and Challenging."
            )

    # Optional: Also update the label's description (if used by screen readers)
        self.difficulty_label.setAccessibleDescription(
         f"Currently selected difficulty is {level}"
         )   
        
    def handle_reset_language(self):
        from main import RootWindow, MainWindow  # Dynamically import to avoid circular imports
        

        
        clear_remember_language()
        # Open language selection dialog (in minimal mode)
        dialog = RootWindow(minimal=True)
        if dialog.exec_() == QDialog.Accepted:
            # Get selected language
            new_lang = dialog.language_combo.currentText()

            # Update global and local language state
            set_language(new_lang)
            self.updated_language = new_lang

            # Show confirmation
            QMessageBox.information(self, "Language Changed",
                                    f"Language changed to {new_lang}. The app will now reload to apply changes.")
            print( "changed language",new_lang)
            # Restart main window with new language
            if self.main_window:
                self.main_window.close()  # Close existing window
                self.main_window = MainWindow(language=new_lang)
                self.main_window.show()

            self.close()  # Close settings dialog


    def accept_settings(self):
        selected_index = self.difficulty_slider.value()
        settings.set_difficulty(selected_index)
        settings.set_language(self.updated_language)
        print(f"[Difficulty] Index set to: {selected_index}")
        self.accept()

    def get_difficulty_index(self):
        return self.difficulty_slider.value()

    def get_selected_language(self):
        return self.updated_language
    