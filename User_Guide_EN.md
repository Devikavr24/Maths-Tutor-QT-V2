# Maths-Tutor User Guide

Maths-Tutor is a free, open-source educational application designed for children aged 5–16, with a primary focus on accessibility for blind and visually impaired students. The application is built from the ground up to be audio-first, meaning it is fully operable using only a keyboard and your ears. Every button, question, and result is announced aloud, ensuring that every student has an equal opportunity to build confidence and mastery in mathematics.

## Table of Contents
1. [Quick Start](#quick-start)
2. [Installation and Setup](#installation-and-setup)
3. [First Launch](#first-launch)
4. [Choosing a Mode](#choosing-a-mode)
5. [Difficulty Levels](#difficulty-levels)
6. [Answering Questions](#answering-questions)
7. [Scoring and Feedback](#scoring-and-feedback)
8. [Keyboard Shortcuts](#keyboard-shortcuts)
9. [Settings](#settings)
10. [Loading Custom Questions](#loading-custom-questions)
11. [Accessibility Features](#accessibility-features)
12. [Troubleshooting](#troubleshooting)
13. [About](#about)

## Quick Start
1. Open Maths-Tutor on your computer.
2. Listen for the language selection announcement and press **Enter** on your preferred language.
3. Use the **Tab** key to move between the three game modes: **Quickplay**, **Game Mode**, and **Learning Mode**. Press **Enter** to select one.
4. Listen as the app reads the first question to you. Type your answer using the number keys.
5. Press **Enter** to submit your answer. If you ever need to hear the question again, press **Control and R** at the same time.

## Installation and Setup
[For Parents and Teachers]
Setting up Maths-Tutor on Linux takes just a few steps. The specific command to install the necessary screen reading components depends on your version of Linux:

*   **Debian, Ubuntu, or Linux Mint**: Use the command **sudo apt install python3 python3-pip espeak-ng python3-pyqt5**
*   **Fedora or Red Hat**: Use the command **sudo dnf install python3 python3-pip espeak-ng python3-qt5**
*   **Arch Linux**: Use the command **sudo pacman -S python python-pip espeak-ng python-pyqt5**
*   **openSUSE**: Use the command **sudo zypper install python3 python3-pip espeak-ng python3-qt5**

Once the system components are ready, finish the setup with these two steps:
1. Open your terminal in the application folder and type **pip install -r requirements.txt** then press **Enter**. This automatically installs the remaining Python libraries.
2. Start the application by typing **python main.py** and pressing **Enter**.

## First Launch
When you start the application for the first time, a language selection window will appear. 
*   Use the **Arrow Keys** to move through the list of languages. The narrator will announce: **English**, **Hindi** (हिंदी), **Malayalam** (മലയാളം), **Tamil** (தமிழ்), **Arabic** (عربي), and **Sanskrit** (संस्कृत).
*   Press **Tab** once to reach the "Remember my selection" checkbox if you want to save this choice for next time. Press the **Space Bar** to check it.
*   Press **Tab** again to reach the **Continue** button and press **Enter**. 
You will then hear "Welcome to Maths Tutor!" followed by your selected language.

### Main Menu and Audio Controls
On the main screen, you will hear sound effects as you navigate between different buttons using the **Tab** key. 

**Audio Mute**
You can reach the **Audio** toggle by pressing **Tab**. The screen reader will announce "Audio Unmuted" if the background music and sound effects are playing, or "Audio Muted" if they are silent. Press **Enter** to switch between the two.

**Theme Toggle**
The application also features a theme toggle in the top-left section (reachable via Tab) that switches between Light and Dark themes. This is primarily for users with partial sight who benefit from different contrast levels.

## Choosing a Mode
You can navigate the main menu by pressing the **Tab** key. Each time you press Tab, the application will announce the next available button. Press **Enter** to select the one you want.

**Quickplay**
In this mode, you will hear a series of arithmetic questions. A timer runs in the background, and the app will provide spoken feedback based on how quickly you answer correctly.

**Learning Mode**
This mode is untimed and designed for building confidence. After selecting it, press **Tab** to hear the topic options, then press **Enter** to choose one:
*   **Story**: You will hear full-sentence word problems, such as: "Jake brought 27 candies to share with his classmates. He gave away 10. How many does Jake have now?"
*   **Time**: Problems involving reading the clock and calculating time.
*   **Currency**: Challenges involving money, shopping, and change.
*   **Distance**: Measurements and length calculation problems.
*   **Bellring**: An interactive activity where you listen to internal bell sounds and count how many times they ring.
*   **Operations**: Standard practice for Addition, Subtraction, Multiplication, Division, and **Percentage**.

**Game Mode**
Designed for the most confident students, this mode begins with a **Warmup Match**. 
*   The app will announce "Warmup Match" and explain the process. 
*   You will hear 14 questions, one from every question type. 
*   The app tracks your speed and ranks your results to perfectly calibrate the main game difficulty. 
*   Press **Enter** on the **Begin Warmup** button to start. 
The main game is competitive, announces a live score, and does not reveal answers if you miss.

## Difficulty Levels
There are five levels of challenge: **Simple**, **Easy**, **Medium**, **Hard**, and **Challenging**. As the difficulty increases, the questions will feature numbers with more digits. You can change your difficulty level at any time in the **Settings** menu.

## Answering Questions
1. When a session begins, the question is read aloud to you automatically.
2. If you missed it or want to check your work, press **Control + R** to repeat the question.
3. Type your answer using the number keys. For Story questions, listen carefully to the full sentence before typing.
4. Press **Enter** to submit.
5. After every outcome—whether you get the answer correct, make a wrong attempt, or the question is skipped—the application will automatically read the next question to you. You do not need to press anything to continue.
6. You have **3 attempts** for every question. After each wrong attempt, the app will repeat the question and you can try again. 
7. After the third failure, the correct answer is read aloud (except in Game Mode), and then the application moves automatically to the next challenge.

## Scoring and Feedback
[For Kids]

**Quickplay**
The faster you answer, the more points you earn!
| Performance | Points |
| :--- | :--- |
| Very Fast 🌟 (4 seconds or less) | 50 points |
| Good 👍 (4 to 12 seconds) | 30 points |
| Slow 🐢 (More than 12 seconds) | 10 points |
| Wrong attempt | -10 points |
| Missed ✗ (3 failures) | 0 points and correct answer read aloud |

**Learning Mode**
In this mode, your score depends on how many tries you take to find the answer.
| Performance | Points |
| :--- | :--- |
| Excellent | 50 points |
| Very Good | 40 points |
| Good | 30 points |
| Not Bad | 20 points |
| Okay | 10 points |
| Wrong attempt | -10 points |

**Your Grade**
At the end of your session, the app announced your final percentage. This is calculated by taking your total score and comparing it to the total points possible.

## Keyboard Shortcuts
| Key | What You Hear / What Happens |
| :--- | :--- |
| **Enter** | Submit your answer, confirm a choice, or move forward in the menu. |
| **Control + R** | The narrator repeats the current question aloud. |
| **Control + ;** | The narrator's voice slows down and re-reads the question. |
| **Alt + ;** | The narrator's voice speeds up. |
| **Tab** | Move forward through the buttons and options on the screen. |
| **Alt + S** | Opens the Settings menu. |
| **Arrow Keys** | Navigate through dropdown lists or difficulty choices in Settings. |
| **Escape** | Cancel an action or close a menu dialog. |
| **Control + Q** | Exit the app. You will hear: "Are you sure you want to exit?". |

## Settings
Press **Alt + S** at any time to open the Settings menu. Press **Tab** to move through the options and use the **Arrow Keys** to change them:
*   **Operator**: Choose Addition, Subtraction, Multiplication, or Division.
*   **Difficulty**: Select a level from Simple to Challenging.
*   **Language and Voice**: Choose the narrator's language and specific voice persona.
*   **Speech Synthesizer**: Pick between engines like espeak-ng, flite, or rh-voice.
*   **Upload**: Import your own Excel (.xlsx) lesson files (press Tab to reach and Enter to select).
*   **Reset to Defaults**: Clears all changes and returns the app to factory settings.

## Loading Custom Questions
[For Teachers]
You can create tailored lessons for your students by creating an Excel (.xlsx) file with a column titled **operands**. Use the following symbols to define your numbers:

| Syntax | Meaning | Example |
| :--- | :--- | :--- |
| * | Any random number | * |
| , | Picks one number from the provided list | 2,4,6,8 |
| : | Random number between two values | 10:20 |
| ; | Multiplies a base by a random range | 2;10:20 |

Downloadable templates are available at the GitHub lessons page: https://github.com/zendalona/maths-tutor/tree/main/lessons

## Accessibility Features
Maths-Tutor is designed to be your primary educational companion, built to the highest accessibility standards:
*   **Always-On Speech**: The built-in text-to-speech engine is natively integrated, meaning every action and result is telegraphed instantly.
*   **Screen Reader Compatible**: The application uses standard interface components that work seamlessly with environmental screen readers.
*   **Digit-by-Digit Reading**: For large or complex numbers, the app can read digits individually to ensure absolute clarity.
*   **High Contrast**: The application inherits high-contrast themes directly from your operating system settings for those with partial sight.

## Troubleshooting
Problem: I cannot hear any audio or speech.
Likely Cause: The speech engine is not installed, or your system volume is muted.
Fix: Install espeak-ng and ensure your primary audio hardware is turned up and unmuted.

Problem: My custom lesson file will not load.
Likely Cause: The file is not an Excel (.xlsx) file or is missing the operands column header.
Fix: Save the file as .xlsx and double-check that the header is spelled correctly.

Problem: I want to exit the application.
Fix: Press **Control + Q**. The app will ask "Are you sure you want to exit?". Press **Tab** to reach **Yes** and then press **Enter** to confirm.

Problem: The application acts incorrectly or doesn't start.
Fix: Open your terminal and run the command **pip install -r requirements.txt** again to ensure all files are correct.

## About
Maths-Tutor is a free and open-source project dedicated to inclusive education for all children.

GitHub Repository: https://github.com/zendalona/maths-tutor
