# 🧮 Maths-Tutor-QT-V2

[![License](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)
[![UI](https://img.shields.io/badge/UI-PyQt5-green.svg)](https://riverbankcomputing.com/software/pyqt/)

**Maths-Tutor-QT-V2** is a desktop-based mathematics learning application built using **PyQt5**.
It provides interactive math practice with **text-to-speech**, **keyboard-first navigation**, and **multiple learning modes**, with a strong focus on accessibility.

---

## ✨ Features

### 🎯 Core Features

* Multiple modes:

  * ⚡ Quickplay
  * 🎮 Game Mode
  * 🎓 Learning Mode
* Question categories:

  * Story
  * Time
  * Currency
  * Distance
  * Bell Ring (audio-based counting)
  * Arithmetic operations (Addition, Subtraction, Multiplication, Division, Percentage)
* Multiple difficulty levels
* Randomized question generation
* Excel-based custom question upload

### ♿ Accessibility

* Text-to-Speech using **pyttsx3**
* Keyboard-only navigation
* Audio feedback for questions and actions
* Screen-reader friendly UI elements

### 🌍 Multilingual Support

* English
* Hindi (हिंदी)
* Malayalam (മലയാളം)
* Tamil (தமிழ்)
* Arabic (عربي)
* Sanskrit (संस्कृत)

(Language selectable at startup and via settings)

---

## 📦 Installation (Windows)

### Prerequisites

- Windows 10 or later  
- Python **3.8+** installed and added to PATH  

---

### Clone the Repository

```bash
git clone https://github.com/Devikavr24/Maths-Tutor-QT-V2.git
cd Maths-Tutor-QT-V2
```

### Install Dependencies
```bash
pip install PyQt5
pip install pandas
pip install pyttsx3
pip install openpyxl
```
---

### Run the Application
```bash
python main.py
```
---

## 🎮 How to Use

### Startup Flow

1. Language selection dialog (optional “Remember my selection”)
2. Mode selection:

   * Quickplay
   * Game Mode
   * Learning Mode
3. Choose difficulty or section
4. Answer questions using the keyboard

---

## 🔊 Audio & Theme

* Background music with mute/unmute toggle
* Sound effects for UI interactions
* Light and Dark theme toggle
* Theme updates applied dynamically

---

## 📁 Project Structure
```bash
Maths-Tutor-QT-V2/
├── main.py
├── pages/
│   ├── shared_ui.py
│   ├── ques_functions.py
├── question/
│   └── loader.py
├── tts/
│   └── tts_worker.py
├── language/
│   └── language.py
├── styles/
│   ├── app.qss
│   ├── main_window.qss
│   └── language_dialog.qss
├── sounds/
├── images/
├── assets/
└── README.md
```
---

## 🧪 Custom Questions (Excel)

* Upload Excel files via the Settings menu
* Questions are processed using the question loader
* Allows extending content without modifying code

---

## ⚙️ Settings

Accessible from within the application:

* Difficulty level
* Language selection
* Theme toggle

All changes apply instantly.

---

## 🛠 Development Notes

* UI refreshes dynamically when language changes
* Text-to-Speech is stopped and reset on navigation
* Background music handled via `QMediaPlayer`
* Modular page-loading architecture

---

## 🤝 Contributing

Contributions are welcome.

Guidelines:

* Do not break accessibility
* Maintain keyboard navigation
* Avoid hard-coded language strings
* Test TTS before submitting changes

---

## 📄 License

This project is licensed under the **GNU General Public License v3.0**.

---

## 🔗 Links

* Repository: [https://github.com/Devikavr24/Maths-Tutor-QT-V2](https://github.com/Devikavr24/Maths-Tutor-QT-V2)
* Issues: [https://github.com/Devikavr24/Maths-Tutor-QT-V2/issues](https://github.com/Devikavr24/Maths-Tutor-QT-V2/issues)
