# 🧮 Maths-Tutor-QT-V2

[![License](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)
[![UI](https://img.shields.io/badge/UI-PyQt5-green.svg)](https://riverbankcomputing.com/software/pyqt/)

**Maths-Tutor-QT-V2** is a desktop-based mathematics learning application built using **PyQt5**.
It provides interactive math practice with **text-to-speech**, **keyboard-first navigation**, and **multiple learning modes**, with a strong focus on accessibility.


![Maths-Tutor Icon](images/icon.png)

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

## � Getting Started

Follow these steps to set up and run Maths-Tutor-QT-V2 on your local machine.

### 1. Clone the Repository
Download the application source code to your computer:
```bash
git clone https://github.com/Devikavr24/Maths-Tutor-QT-V2.git
cd Maths-Tutor-QT-V2
```

### 2. Windows Setup

**Prerequisites:**
* Windows 10 or later
* [Python 3.8+](https://www.python.org/downloads/) (Ensure "Add Python to PATH" is checked during installation)

**Installation Steps:**
1. Open a terminal (Command Prompt or PowerShell) in the project folder.
2. Install the required Python dependencies:
   ```cmd
   pip install -r requirements.txt
   ```
3. **(Optional but Recommended)** Install the offline TTS engine for robust language support:
   * Download and run the installer from the [eSpeak-NG Releases Page](https://github.com/espeak-ng/espeak-ng/releases).

**Running the Application:**
```cmd
python main.py
```

---

### 3. Linux (Ubuntu/Debian) Setup

**Prerequisites:**
* Python 3.8+
* `pip` package manager

**Installation Steps:**
1. Open your terminal in the project folder.
2. Install the required Python dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```
3. Install the `espeak-ng` package for native TTS voice support:
   ```bash
   sudo apt update
   sudo apt install espeak-ng
   ```

**Running the Application:**
```bash
python3 main.py
```

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
```text
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

## 🗑️ Uninstall / Remove Maths Tutor

If you no longer need **Maths Tutor**, you can remove it using the steps below.

### Windows

If you cloned the repository and ran it locally, the application is **not installed system-wide**.

#### Option 1: Using File Explorer (Recommended)
- Navigate to the folder where you cloned the project
- Delete the `Maths-Tutor-QT-V2` folder

#### Option 2: Using Command Prompt (cmd.exe)
```bat
rmdir /s /q Maths-Tutor-QT-V2
```
## 📄 License

This project is licensed under the **GNU General Public License v3.0**.

---

## 🔗 Links

* Repository: [https://github.com/Devikavr24/Maths-Tutor-QT-V2](https://github.com/Devikavr24/Maths-Tutor-QT-V2)
* Issues: [https://github.com/Devikavr24/Maths-Tutor-QT-V2/issues](https://github.com/Devikavr24/Maths-Tutor-QT-V2/issues)
