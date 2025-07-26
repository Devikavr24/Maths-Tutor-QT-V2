import os, shutil
import pandas as pd
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QInputDialog, QHBoxLayout, QWidget ,QVBoxLayout ,QGridLayout
from question.loader import  QuestionProcessor
# pages/ques_functions.py

from pages.shared_ui import (
    create_colored_widget,
    create_label,
    create_menu_button,
    create_vertical_layout,
    create_dynamic_question_ui,
    create_entry_ui, apply_theme,
    QuestionWidget
)

from question.loader import QuestionProcessor
import os, shutil
import pandas as pd

from PyQt5.QtWidgets import QFileDialog, QMessageBox, QInputDialog,QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,QPushButton, QLabel, QSizePolicy
from PyQt5.QtCore import Qt

from language.language import tr



def load_pages(section_name, back_callback, difficulty_index,
               main_window=None):

    page = create_colored_widget("#e0f7fa")
 
    widgets = []
 
    # 👉 Custom logic for "Operations"
    if section_name.lower() == "operations":
        title = create_label("Choose an Operation", font_size=22, bold=True)
        title = create_label(tr("Choose an Operation"), font_size=22, bold=True)
        title.setAlignment(Qt.AlignCenter)

        grid = QGridLayout()
        grid.setSpacing(20)

        operations = ["Addition", "Subtraction", "Multiplication", "Division", "Remainder", "Percentage"]

        for i, sub in enumerate(operations):
            translated=tr(sub)
            btn = create_menu_button(translated, lambda _, s=sub: main_window.load_section(s))
            btn.setFixedSize(180, 60)
            grid.addWidget(btn, i // 2, i % 2)  # 2 columns

        wrapper = QWidget()
        wrapper.setLayout(grid)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.addWidget(title)
        layout.addSpacing(20)
        layout.addWidget(wrapper)
        layout.addSpacing(30)

        page.setLayout(layout)
        return page

    # ✅ For other sections
    return create_dynamic_question_ui(section_name, difficulty_index, back_callback,main_window=main_window)

uploaded_df = None

def upload_excel(parent_widget):
    

    

    file_path, _ = QFileDialog.getOpenFileName(parent_widget, "Select Excel File", "", "Excel Files (*.xlsx)")
    if not file_path:
        return

 
    df = pd.read_excel(file_path)
    global uploaded_df
    uploaded_df = df

    print(uploaded_df)
  

    required = {"question", "operands", "equation"}
    if not required.issubset(df.columns):
        QMessageBox.critical(parent_widget, "Invalid File", "Excel must have columns titled: question, operands, equation")
        return

    #os.makedirs(exist_ok=True)
        #dest_path = os.path.join( "question.xlsx")
        #shutil.copyfile(file_path, dest_path)
    QMessageBox.information(parent_widget, "Success", "Questions uploaded successfully!")
    main_window=parent_widget
    entry_ui = create_entry_ui(main_window)
    apply_theme(entry_ui, main_window.current_theme)  
    main_window.setCentralWidget(entry_ui)
    




def load_entry_page(main_window):
        entry_ui = create_entry_ui(main_window)
        main_window.setCentralWidget(entry_ui)

  # global storage

def start_uploaded_quiz(main_window):
    global uploaded_df
    if uploaded_df is None:
        print('no uploaded_df')
        return

    processor = QuestionProcessor("custom", 0)  # pass dummy type and difficulty
    print('dummy value passed to init of processor')
    processor.df = uploaded_df  # manually inject uploaded data
    print(processor.df)

    question_widget = QuestionWidget(processor, window=main_window)
    apply_theme(question_widget, main_window.current_theme)
    main_window.setCentralWidget(question_widget)
   