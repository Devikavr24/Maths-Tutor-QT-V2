<div style="font-family: Arial, sans-serif; font-size: 11pt; text-align: justify;">

<br><br><br><br><br>
<h1 align="center">Maths-Tutor User Guide</h1>
<h3 align="center">Version 2.0</h3>
<br><br><br><br><br>

<div style="page-break-after: always;"></div>

## Table of Contents
1. [Introduction to Maths-Tutor](#1-introduction-to-maths-tutor)
2. [System Requirements & Installation](#2-system-requirements--installation)
3. [Getting Started](#3-getting-started)
4. [Practice Mode](#4-practice-mode)
5. [Selecting Operator and Difficulty](#5-selecting-operator-and-difficulty)
6. [Answering Questions](#6-answering-questions)
7. [Scoring & Appreciation](#7-scoring--appreciation)
8. [Settings (Alt + S)](#8-settings-alt--s)
9. [Loading a Custom Question File](#9-loading-a-custom-question-file)
10. [Accessibility Features](#10-accessibility-features)
11. [Keyboard Shortcuts](#11-keyboard-shortcuts)
12. [Troubleshooting](#12-troubleshooting)

<div style="page-break-after: always;"></div>

## 1. Introduction to Maths-Tutor
Welcome to Maths-Tutor, a free and open-source educational application designed to make learning mathematics engaging and accessible. Maths-Tutor is specifically developed for children aged 5 to 16, with a strong focus on accessibility for visually impaired users.

Built from the ground up to be an audio-first experience, the application seamlessly integrates with standard systems and provides spoken feedback for every action. Whether used at home by parents, or in schools by teachers, Maths-Tutor ensures that every student has an equal opportunity to thrive and build confidence in their mathematical skills.

## 2. System Requirements & Installation
Maths-Tutor is a lightweight application designed to run smoothly on modern systems.

**Primary Platform:** Linux
**Framework:** Python with PyQt

> **Note:** While the application is Python-based and cross-platform in nature, it has been primarily designed and tested on Linux environments, particularly those configured for accessibility.

**Dependencies:**
- Python 3.x
- PyQt5 or PyQt6
- A supported Text-to-Speech (TTS) engine: `espeak-ng`, `flite`, or `rh-voice`

**Installation & Launching:**
Ensure you have the required dependencies installed on your Operating System. To launch the application, open a terminal window in the application folder and run:
`python main.py`

## 3. Getting Started
When you launch Maths-Tutor for the first time, you will be greeted with a **Language Selection** dialog. This allows you to choose the preferred language for the application's interface and spoken feedback. You can check the "Remember Selection" option so that the application automatically loads your preferred language on future launches without asking again.

Once the language is selected, you are taken to the main game page. This clean, distraction-free environment is where the mathematical challenges take place. 

To begin a session, simply press the **Enter** key.

## 4. Practice Mode
Maths-Tutor provides a structured Practice Mode, strictly designed for step-by-step learning.

Difficulty progresses in a linear fashion through four distinct tiers: Easy, Medium, Champion, and Legend. The available mathematical operations you can practice include Addition, Subtraction, Multiplication, and Division. As the child masters one tier and becomes comfortable with the current speed and complexity, the number of digits in the questions progressively increases, ensuring a gentle but firm learning curve.

## 5. Selecting Operator and Difficulty
By default, the application will select starting values for you, but you can tailor the experience to your specific needs.
- **Available Operators:** Addition, Subtraction, Multiplication, Division.
- **Difficulty Levels:** You can specify the digit-level of the questions, such as Simple (1-digit), Medium (2-digit), Hard (3-digit), and so forth.

The application conveniently remembers your last selected operator and difficulty settings, meaning you can easily pick up right where you left off on your next session.

## 6. Answering Questions
Maths-Tutor aims to make the input process as intuitive as possible:
- **Submitting Answers:** Simply type the answer using your keyboard and press **Enter** to submit.
- **Attempts:** You are allowed up to 3 attempts per question. If the correct answer is not found after the 3rd attempt, the application will gently provide the correct answer before moving you to the next question.
- **Speed Feedback:** To encourage fluency, feedback is given based on response time. You may hear varying levels of praise such as Excellent, Very Good, Good, Fair, or Okay.
- **Verbose Mode (Shift Key):** If you are unsure of the number being spoken, pressing **Shift** will announce the digits individually (e.g., "one, two, three" instead of "one hundred and twenty-three").
- **Repeat Question (Space Key):** Missed the question? Just press **Space** to hear it repeated aloud.

## 7. Scoring & Appreciation
The scoring system is designed to reward both accuracy and speed, fostering quick mental recall.

**Score Table per Question:**
- Excellent = 50 points
- Very Good = 40 points
- Good = 30 points
- Fair = 20 points
- Okay = 10 points
- Wrong attempt = -10 points

**Appreciation Time Thresholds:**
The application scales the expected response time based on the complexity of the question. Your speed relative to this expected time determines your appreciation level:
- ≤ 50% time = **Excellent**
- ≤ 75% time = **Very Good**
- ≤ 100% time = **Good**
- ≤ 125% time = **Fair**
- \> 125% time = **Okay**

**Final Grade Formula:**
At the end of a session, a final percentage grade is calculated using the following formula:
`(Total Score × 100) / (50 × Number of Questions Attempted)`

## 8. Settings (Alt + S)
You can configure the application at any time by pressing **Alt + S** to open the Settings menu. The interface is fully accessible via keyboard navigation.

From the Settings menu, you can configure:
- **Operator & Difficulty:** Adjust the mathematical operation and the number of digits.
- **Speech Synthesizer:** Choose your preferred TTS engine (`espeak-ng`, `flite`, or `rh-voice`).
- **Language & Voice:** Select the target language and the specific voice persona for the narrator.
- **Load Question File:** Import your own tailored list of questions.
- **Reset Defaults:** A quick option to reset your language, operator, difficulty, and TTS settings back to factory defaults.

Once your preferences are configured, simply press the **Start** button to restart the game with your new settings engaged.

## 9. Loading a Custom Question File
Teachers and parents can create personalized lesson plans by loading a custom text file. Maths-Tutor includes several built-in lessons, which you can find at: [Built-in Lessons](https://github.com/zendalona/maths-tutor/tree/main/lessons)

**File Constraints:**
- Must be a standard `.txt` file.
- Strict format of one question per line.
- **No blank lines** are permitted anywhere in the document.

**Question Format:**
Each line must follow this precise structure:
`expression===time_in_seconds===bell_toggle`
*(Where `bell_toggle` is `1` to play a bell sound upon completion or `0` for none).*

**Operand Methods:**
You have deep flexibility in determining the operands for your custom equations:
- **Fixed number:** e.g., `4`
- **Comma-separated list:** e.g., `2,4,6,8`
- **Colon range:** e.g., `10:20` (a random number systematically picked between 10 and 20)
- **Semicolon multiplier range:** e.g., `2;10:20` (a random output from multiplying 2 by random numbers from 10 to 20, creating even responses)

> **Example:**
> `random(2;10:20)*random(2,4,6,8)===30===1`
> *This will ask a multiplication question where the first number is an even number from 10-20, the second number is chosen from 2, 4, 6, 8, the timer allows 30 seconds for the answer, and a bell will chime when the question is completed.*

## 10. Accessibility Features
Maths-Tutor is fundamentally an accessibility-first tool. Rather than bolting accessibility onto a visual UI interface, the application was built with the auditory experience given utmost priority.

- **Built-in TTS:** Integrated natively with robust speech synthesizers (`espeak-ng`, `flite`, `rh-voice`) to ensure the application never goes mute, even if external screen readers fail.
- **Screen Reader Compatibility:** The UI relies on standard components seamlessly designed to communicate with OS-level screen readers.
- **Audio-first Feedback Design:** Every action, validation, and transition is effectively telegraphed via clear, concise spoken audio and sound cues.
- **Verbose Number Reading:** Long, complex numbers can be broken down digit-by-digit for ultimate clarity.
- **High Contrast Support:** Inherits theming natively from OS-level system settings, ensuring visual ease when needed.

## 11. Keyboard Shortcuts
For maximum efficiency and screen reader compatibility, Maths-Tutor can be completely operated via the keyboard.

| Key / Combination | Action |
| --- | --- |
| **Enter** | Start session / Submit answer |
| **Space** | Repeat the current question loudly and clearly |
| **Shift** | Verbose mode (read previous number digit-by-digit) |
| **Alt + S** | Open the Settings menu |
| **Apostrophe (')** | Increase speech synthesizer voice rate |
| **Semicolon (;)**| Decrease speech synthesizer voice rate |

## 12. Troubleshooting

> **Note:** Troubleshooting steps involving environmental configurations may vary slightly depending on your specific Linux distribution or Operating System architecture.

- **No audio/speech output:**
  Check that your selected TTS engine (`espeak-ng`, `flite`, or `rh-voice`) is correctly installed on your operating system. If you are using Linux, ensure your primary audio hardware sink is unmuted and the volume is up.
- **Question file not loading:**
  Double-check your custom `.txt` formatting. Ensure each line adhering to the `expression===time===bell` syntax contains no extra spaces around equality markers, and heavily scrutinize the document to verify **no blank lines** are present at the beginning, middle, or end of the file.
- **Visual Theme not applying correctly:**
  Maths-Tutor inherits its look and styling from system accessibility parameters. Check your OS-level appearance settings in Linux (such as GTK/Qt UI themes and high-contrast toggles) to ensure they are configured correctly.

</div>
