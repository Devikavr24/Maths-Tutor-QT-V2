# Maths-Tutor User Guide

Maths-Tutor is a free, open-source mathematics learning application designed for blind and visually impaired children. 
Built entirely around keyboard and voice, it requires no mouse or screen to operate. Every question, result, and menu option is spoken aloud through a built-in text-to-speech engine, making independent learning possible for every child.
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
3. Use the **Tab** key to move between the three game modes: **Quickplay**, **Game Mode**, and **Learning Mode**. Press **Space Bar** or **Enter** to select one.
4. Listen as the app reads the first question to you. Type your answer using the number keys.
5. Press **Enter** to submit your answer. (Note: Only the Enter key submits answers; the Space Bar does not). If you ever need to hear the question again, press **Control and R** at the same time.

## Installation and Setup
[For Parents and Teachers]
Setting up Maths-Tutor takes just a few steps:

1. Run: pip install -r requirements.txt
2. Install espeak-ng via your system software manager
3. Run: python main.py

## First Launch
When you start the application for the first time, a language selection window will appear. 
*   Use the **Arrow Keys** to move through the list of languages. The narrator will announce: **English**, **Hindi** (हिंदी), **Malayalam** (മലയാളം), **Tamil** (தமிழ்), **Arabic** (عربي), and **Sanskrit** (संस्कृत).
*   Press **Tab** once to reach the "Remember my selection" checkbox. Press the **Space Bar** to check/uncheck it.
*   Press **Tab** again to reach the **Continue** button and press **Space Bar** or **Enter**. (Note: As **Continue** is the default button, you can also press **Enter** at any time while the dialog is open to confirm).
You will then hear "Welcome to Maths Tutor!" followed by your selected language.

### Main Menu and Audio Controls
On the main screen, you will hear sound effects as you navigate between different buttons using the **Tab** key. 

**Audio Mute**
You can reach the **Audio** toggle by pressing **Tab**. The screen reader will announce "Audio Unmuted" if the background music and sound effects are playing, or "Audio Muted" if they are silent. Press **Space Bar** or **Enter** to switch between the two.

**Theme Toggle**
The application also features a theme toggle in the top-left section (reachable via Tab) that switches between Light and Dark themes. This is primarily for users with partial sight who benefit from different contrast levels.

## Choosing a Mode
You can navigate the main menu by pressing the **Tab** key. Each time you press Tab, the application will announce the next available button. Press **Space Bar** or **Enter** to select the one you want. (Starting from the top, the order is: Theme Toggle, Quickplay, Game Mode, Learning Mode, Audio Toggle, Upload, and Settings).

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
*   Press **Space Bar** (as the button is focused automatically) or **Enter** on the **Begin Warmup** button to start. 
The main game is competitive, announces a live score, and does not reveal answers if you miss.

## Difficulty Levels
There are five levels of challenge: **Simple**, **Easy**, **Medium**, **Hard**, and **Challenging**. As the difficulty increases, the questions will feature numbers with more digits. You can change your difficulty level at any time in the **Settings** menu.

## Answering Questions
1. When a session begins, the question is read aloud to you automatically.
2. If you missed it or want to check your work, press **Control + R** to repeat the question.
3. Type your answer using the number keys. For Story questions, listen carefully to the full sentence before typing.
4. Press **Enter** to submit. (Note: Only **Enter** submits the answer; **Space** is not used for submission).
5. After every outcome—whether you get the answer correct, make a wrong attempt, or the question is skipped—the application will automatically read the next question to you. You do not need to press anything to continue.
6. You have **3 attempts** for every question. After each wrong attempt, the app will repeat the question and you can try again. 
7. After the third failure, the correct answer is read aloud (except in Game Mode), and then the application moves automatically to the next challenge.

## Scoring and Feedback
Only Game Mode has a scoring system (the exact scoring logic requires confirmation from the code before documenting).

There is no point system, score table, grade, or percentage calculation at the end of Quickplay or Learning Mode sessions.

## Keyboard Shortcuts
| Key | What You Hear / What Happens |
| :--- | :--- |
| **Enter** | Submit your answer (during a session) or confirm a choice (default button). |
| **Space Bar** | Activate a focused button or check/uncheck a checkbox. |
| **Control + R** | The narrator repeats the current question aloud. |
| **Control + ;** | The narrator's voice slows down and re-reads the question. |
| **Alt + ;** | The narrator's voice speeds up. |
| **Tab** | Move forward through the buttons and options on the screen. |
| **Arrow Keys** | Navigate through dropdown lists, the language list, or the difficulty slider. |
| **Escape** | Cancel an action or close a menu dialog. |
| **Control + Q** | Exit the app. You will hear: "Are you sure you want to exit?". |

## Settings
Use the **Tab** key to reach the **Settings** button in the main menu footer and press **Space Bar**. Inside Settings, the **Tab order** is: Difficulty Slider, Reset Language, Help, About, OK, and Cancel.
*   **Difficulty**: Use the **Left and Right Arrow Keys** to change the level from Simple to Challenging.
*   **Language**: Select the **Reset Language** button (via Tab and Space) to open the language choice window.
*   **OK / Cancel**: Press **Tab** to reach these buttons and press **Space Bar** or **Enter** to confirm or discard your changes.

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
Fix: Press **Control + Q**. The app will ask "Are you sure you want to exit?". Press **Tab** to reach **Yes** and then press **Space Bar** to confirm. (Note: Pressing **Enter** will activate **No** by default).

Problem: The application acts incorrectly or doesn't start.
Fix: Open your terminal and run the command **pip install -r requirements.txt** again to ensure all files are correct.

## About
Maths-Tutor is a free and open-source project dedicated to inclusive education for all children.

GitHub Repository: https://github.com/Devikavr24/Maths-Tutor-QT-V2