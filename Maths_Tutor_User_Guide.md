# Maths-Tutor User Guide

Maths-Tutor is a free, open-source educational tool designed to make mathematics engaging and accessible for children aged 5–16. Built with a focus on inclusion, this audio-first application provides a distraction-free environment where students can build confidence and speed in mental arithmetic through spoken feedback and interactive challenges.

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
1. Open the application on your computer.
2. Select your preferred language and press the Continue button.
3. Choose a game mode from the main menu using your mouse or the Tab and Enter keys.
4. Listen to the question, type your answer using the number keys, and press Enter to submit.
5. If you need to hear the question again, press the Control and R keys together.

## Installation and Setup
[For Parents and Teachers]
Follow these simple steps to get Maths-Tutor running on your Linux computer:
1. Install Python 3 using your system's software manager.
2. Install the PyQt5 or PyQt6 library.
3. Install a text-to-speech engine; espeak-ng is recommended for the best experience.
4. Open your computer's terminal window inside the folder where the app is located.
5. Type the command python main.py and press Enter.

## First Launch
When you open the app for the first time, a language selection window will appear. You can choose from several languages for both the text and the spoken voice. If you check the box to remember your selection, the app will skip this window next time and take you straight to the main screen.

## Choosing a Mode
Maths-Tutor features three distinct ways to learn and play:

**Learn Mode**
Suited for beginners and younger children. This mode is untimed, allowing kids to focus entirely on accuracy without any pressure. It is the perfect place to build foundational confidence.

**Quick Play Mode**
Designed for kids who have mastered the basics and are ready to work on their speed. This mode is timed and rewards quick thinking with high-energy feedback.

**Game Mode**
Built for confident kids who want a real challenge. When you start, the app asks several warmup questions to find out exactly how good you are. It then uses those results to set a perfectly calibrated difficulty level. There is a live score on the screen, a ticking clock, and no answers are revealed if you miss—it is a true test of skill!

## Difficulty Levels
The app moves in a linear fashion through five levels: **Simple**, **Easy**, **Medium**, **Hard**, and **Challenging**. As you move up, the questions use more digits and the mathematical operations become more complex, ensuring that the challenge keeps pace with your child's growth.

## Answering Questions
To provide an answer, type the numbers on your keyboard and press the **Enter** key. You are given 3 attempts for every question. In Learning and Practice modes, the correct answer will be revealed if the third attempt is wrong. If you missed what the narrator said, simply press **Ctrl + R** to repeat the current question as many times as you need.

## Scoring and Feedback
[For Kids]

**Practice Mode**
In this mode, the faster you answer, the better your reward!
| Performance | Points |
| :--- | :--- |
| Very Fast 🌟 | 50 points |
| Good 👍 | 30 points |
| Slow 🐢 | 10 points |
| Wrong attempt | -10 points |
| Missed ✗ | 0 points |

**Learning Mode**
Because there is no timer, your score is based on how many tries you take to get it right.
| Performance | Points |
| :--- | :--- |
| Excellent | 50 points |
| Very Good | 40 points |
| Good | 30 points |
| Not Bad | 20 points |
| Okay | 10 points |
| Wrong attempt | -10 points |

**Final Grade**
At the end of your session, the app gives you a percentage grade. It is calculated by taking your total score and dividing it by the maximum possible points you could have earned.

## Keyboard Shortcuts
| Key | What It Does |
| :--- | :--- |
| Enter | Submit your answer or move to the next screen |
| Ctrl + R | Repeat the current question out loud |
| Ctrl + ; | Slow down the speed of the narrator's voice |
| Alt + ; | Speed up the speed of the narrator's voice |
| Ctrl + Q | Exit the application completely |
| Alt + S | Open the Settings menu |

## Settings
[For Parents and Teachers]

**Operator**
Choose which type of math to practice: Addition, Subtraction, Multiplication, or Division.

**Difficulty**
Move the slider to set the complexity level from Simple to Challenging manually.

**Language and Voice**
Select the interface language and choose from available narrator voices.

**Speech Synthesizer**
Choose between different text-to-speech engines like espeak-ng, flite, or rh-voice based on what is installed on your system.

**Upload Custom File**
Use this to select an Excel file from your computer that contains your own custom-made questions.

**Reset to Defaults**
A one-click option to clear all changes and return the app to its original factory settings.

## Loading Custom Questions
[For Teachers]
You can create your own lessons by saving an Excel (.xlsx) file with a column titled **operands**. Use the following symbols to tell the app how to generate numbers:

| Syntax | Meaning | Example |
| :--- | :--- | :--- |
| * | Any random number from the default set | * |
| , | Pick one specific number from your list | 2,4,6,8 |
| : | Random number between two values | 10:20 |
| ; | Multiply a base number by a random range | 2;10:20 |

You can find pre-made lesson files to use as templates at the official GitHub lessons page: https://github.com/zendalona/maths-tutor/tree/main/lessons

## Accessibility Features
Maths-Tutor is designed from the ground up to be inclusive:
*   **Built-in TTS**: Integrated speech engines ensure audio feedback is always available.
*   **Screen Reader Friendly**: Built using standard components that work seamlessly with environmental screen readers.
*   **Audio-First Design**: Every button, error, and success is spoken aloud, making a screen almost unnecessary.
*   **Verbose Reading**: For ultimate clarity, users can hear numbers read as individual digits.
*   **Visual Display**: High contrast and font sizes are inherited directly from your operating system settings.

## Troubleshooting
Problem: There is no audio or speech.
Likely Cause: A speech engine is not installed or your system volume is muted.
Fix: Ensure espeak-ng or flite is installed and check your computer's audio settings.

Problem: A custom question file will not load.
Likely Cause: The file is not in the correct Excel (.xlsx) format or is missing the operands column.
Fix: Check the file type and ensure the table headers are spelled correctly.

Problem: The app theme looks wrong or is hard to see.
Likely Cause: Your operating system theme is not configured for high contrast.
Fix: Adjust your system's visual or accessibility settings to increase contrast.

Problem: The app will not start when running the launch command.
Likely Cause: Python or the PyQt library is missing.
Fix: Reinstall Python 3 and the PyQt5 or PyQt6 packages.

## About
Maths-Tutor is a free and open-source project dedicated to making math accessible for everyone.

GitHub: https://github.com/zendalona/maths-tutor
