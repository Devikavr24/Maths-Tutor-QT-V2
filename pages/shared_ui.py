# pages/shared_ui.py

from PyQt5.QtWidgets import ( QWidget, QLabel, QHBoxLayout, QPushButton,
                              QVBoxLayout,QSizePolicy, QDialog, QSlider, QDialogButtonBox
                              ,QSpacerItem,QLineEdit)

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor, QIntValidator
from question.loader import QuestionProcessor
from time import time
import random
DIFFICULTY_LEVELS = ["Very Easy", "Easy", "Medium", "Hard", "Very Hard"]


from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

def create_entry_ui(main_window) -> QWidget:
    entry_widget = QWidget()
    layout = QVBoxLayout()
    layout.setAlignment(Qt.AlignCenter)

    label = QLabel("Click below to start the quiz")
    label.setFont(QFont("Arial", 24))
    label.setAlignment(Qt.AlignCenter)

    button = QPushButton("Start")
    button.setFont(QFont("Arial", 16))
    button.setFixedSize(200, 50)
    button.setStyleSheet("background-color: #28a745; color: white; border-radius: 8px;")

    def start_quiz():
        print("Start button clicked")  # ✅ DEBUG POINT
        from pages.ques_functions import start_uploaded_quiz
        start_uploaded_quiz(main_window)

    button.clicked.connect(start_quiz)

    layout.addWidget(label)
    layout.addSpacing(20)
    layout.addWidget(button, alignment=Qt.AlignCenter)

    entry_widget.setLayout(layout)
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
    layout.setContentsMargins(10, 10, 10, 10)
    layout.addStretch()

    for name in names:
        btn = QPushButton(name)
        btn.setFixedSize(*size)
        btn.setProperty("class", "footer-button")
        if callbacks and name in callbacks:
            btn.clicked.connect(callbacks[name])
        layout.addWidget(btn)

    footer.setLayout(layout)
    return footer


def create_back_button(callback) -> QPushButton:
    back_btn = QPushButton("HOME")
    back_btn.setFixedSize(150, 40)
    back_btn.setProperty("class", "menu-button")
    back_btn.clicked.connect(callback)
    return back_btn



def create_answer_input(width=300, height=40, font_size=14) -> QLineEdit:
    input_box = QLineEdit()
    input_box.setFixedSize(width, height)
    input_box.setAlignment(Qt.AlignCenter)
    input_box.setPlaceholderText("Enter your answer")
    input_box.setFont(QFont("Arial", font_size))
    input_box.setValidator(QIntValidator(0, 1000000))  # only positive integers
    input_box.setStyleSheet("""
        QLineEdit {
            border: 2px solid #ccc;
            border-radius: 10px;
            padding: 6px 10px;
        }
        QLineEdit:focus {
            border: 2px solid #0078d7;
            background-color: #f0f8ff;
        }
    """)
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
    def __init__(self, processor,window=None):
        super().__init__()
        self.processor = processor
        self.answer = None
        self.start_time = time()
        self.max_questions = 10
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)
        self.main_window = window
        self.init_ui()

    def init_ui(self):
        self.question_area = QWidget()
        question_layout = QVBoxLayout()
        question_layout.setAlignment(Qt.AlignCenter)
        self.question_area.setLayout(question_layout)

        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(QFont("Arial", 16))
        self.label.setWordWrap(True)

        question_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        question_layout.addWidget(self.label)
        question_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # ✅ Styled input box (your own function)
        self.input_box = create_answer_input()
        self.input_box.returnPressed.connect(self.check_answer)

        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setFont(QFont("Arial", 12))

        #🧱 Assemble the main layout
        self.layout.addWidget(self.question_area)
        self.layout.addSpacing(20)
        self.layout.addWidget(self.input_box, alignment=Qt.AlignCenter)
        self.layout.addSpacing(10)
        self.layout.addWidget(self.result_label)
        self.layout.addStretch()

        self.end_button = QPushButton("End Session")
        self.end_button.setStyleSheet("background-color: red; color: white; padding: 10px;")
        self.end_button.setFixedWidth(150)
        self.end_button.clicked.connect(self.end_session)
        self.layout.addWidget(self.end_button, alignment=Qt.AlignCenter)

        self.layout.addStretch()
        

        self.load_new_question()
    

    def end_session(self):
        #if hasattr(self, 'bg_player') and self.bg_player is not None:
    
        self.main_window.bg_player.stop()   # or .stop() if you want to fully stop it
        print("[BG MUSIC] Stopped due to end session.")
        if self.main_window:
            from main import MainWindow  # Import your section menu window
            self.main_window.setCentralWidget(MainWindow(self.main_window))



    
    def load_new_question(self):
        if self.processor.total_attempts >= self.max_questions:
            self.show_final_score()
            return
        question_text, self.answer = self.processor.get_questions()
        self.start_time = time()
        self.label.setText(question_text)
        self.input_box.setText("")  # ✨ Clear only the input
        self.result_label.setText("")
    def show_final_score(self):
                self.result_label.setText(
                    "🎉 Quiz Finished!"
                )
                print("Final Score:", self.processor.correct_answers, "/", self.processor.total_attempts)
                sound_index = random.randint(1, 3)
                self.main_window.play_sound(f"finished-{sound_index}.mp3")
            
    def check_answer(self):
        try:
            user_input = self.input_box.text().strip()
            user_answer = float(user_input)
            elapsed = time() - self.start_time

            correct = float(user_answer) == float(self.answer)
            self.processor.submit_answer(user_answer, self.answer, elapsed)

            if correct:
                self.result_label.setText("✅ Correct!")



               
                sound_index = random.randint(1, 3)
                
                if elapsed < 5:
                    if self.main_window and callable(getattr(self.main_window, "play_sound", None)):
                        self.main_window.play_sound(f"excellent-{sound_index}.mp3")
                elif elapsed < 10:
                    if self.main_window:
                        self.main_window.play_sound(f"very-good-{sound_index}.mp3")
                elif elapsed < 15:
                    if self.main_window:
                        self.main_window.play_sound(f"good-{sound_index}.mp3")
                elif elapsed < 20:
                    if self.main_window:
                        self.main_window.play_sound(f"not-bad-{sound_index}.mp3")
                else:
                    if self.main_window:
                        self.main_window.play_sound(f"okay-{sound_index}.mp3")

                self.processor.retry_count = 0
                self.load_new_question()  # ✨ Just update content

            else:
                self.processor.retry_count += 1
                sound_index = random.randint(1, 3)
                if self.processor.retry_count == 1:
                    self.main_window.play_sound(f"wrong-anwser-{sound_index}.mp3")
                else:
                    self.main_window.play_sound(f"wrong-anwser-repeted-{sound_index}.mp3")
                    
                
                if self.processor.retry_count < 3:
                    self.result_label.setText(f"❌ Wrong. Try again ({self.processor.retry_count}/3)")
                else:
                    self.result_label.setText("❌ Wrong. Moving to next question.")
                    self.processor.retry_count = 0
                    self.load_new_question()

        except Exception as e:
            self.result_label.setText(f"Error: {str(e)}")



def create_dynamic_question_ui(section_name, difficulty_index, back_callback,window=None):
    container = QWidget()
    layout = QVBoxLayout()
    layout.setAlignment(Qt.AlignTop)
    container.setLayout(layout)

    processor = QuestionProcessor(section_name, difficulty_index)
    processor.process_file()
    
    question_widget = QuestionWidget(processor,window=window)

    layout.addWidget(question_widget)

    # Back Button at the bottom
    back_btn = QPushButton("HOME")
    back_btn.setFixedSize(150, 40)
    back_btn.clicked.connect(back_callback)
    layout.addWidget(back_btn, alignment=Qt.AlignCenter)

    return container
class SettingsDialog(QDialog):
    def __init__(self, parent=None, initial_difficulty=1, main_window=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setFixedSize(400, 220)

        self.main_window = main_window
        self.updated_language = main_window.language if main_window else "English"

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
        self.difficulty_slider.setValue(initial_difficulty)
        self.difficulty_slider.valueChanged.connect(self.update_difficulty_label)

        self.difficulty_label = create_label(DIFFICULTY_LEVELS[initial_difficulty], font_size=12)

        # 🔁 Reset Language Button
        self.language_reset_btn = QPushButton("Reset Language")
        self.language_reset_btn.setFixedHeight(30)
        self.language_reset_btn.clicked.connect(self.handle_reset_language)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept_settings)
        button_box.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(create_label("Select Difficulty:", font_size=12, bold=False))
        layout.addWidget(self.difficulty_slider)
        layout.addWidget(self.difficulty_label)
        layout.addSpacing(15)
        layout.addWidget(self.language_reset_btn)
        layout.addSpacing(10)
        layout.addWidget(button_box)
        self.setLayout(layout)

    def update_difficulty_label(self, index):
        self.difficulty_label.setText(DIFFICULTY_LEVELS[index])

    def handle_reset_language(self):
        from main import RootWindow, MainWindow # Dynamically import to avoid circular imports

        dialog = RootWindow(minimal=True)
        if dialog.exec_() == QDialog.Accepted:
            new_lang = dialog.language_combo.currentText()
            self.updated_language = new_lang
            print(f"[Language Reset] New language: {new_lang}")

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
        

