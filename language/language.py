# language/language.py
import os
import gettext


selected_language = "en"

def _get_config_file_path():
    app_data_dir = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "MathsTutor")
    os.makedirs(app_data_dir, exist_ok=True)
    return os.path.join(app_data_dir, "selected_lang.txt")

def update_language():
    global _

    gettext.bindtextdomain("messages","locales")
    gettext.textdomain("messages")
    print(f"\n{selected_language}\n")
    lang = gettext.translation("messages", localedir="locales", languages=[selected_language], fallback=True)
    lang.install()


def save_selected_language_to_file(lang):
    print("save to file function called")
    with open(_get_config_file_path(), "w", encoding="utf-8") as f:
        f.write(lang)

def get_saved_language():
    config_file = _get_config_file_path()
    if os.path.exists(config_file):
        with open(config_file, "r", encoding="utf-8") as f:
            return f.read().strip()
    return None

def set_language(lang):
    global selected_language
    selected_language = lang
    update_language()

def clear_remember_language():
    config_file = _get_config_file_path()
    if os.path.exists(config_file):
        os.remove(config_file)

def localize_numbers(text):
    if not isinstance(text, str):
        text = str(text)
    
    num_maps = {
        "hi_IN": {'0': '०', '1': '१', '2': '२', '3': '३', '4': '४', '5': '५', '6': '६', '7': '७', '8': '८', '9': '९'},
        "mr_IN": {'0': '०', '1': '१', '2': '२', '3': '३', '4': '४', '5': '५', '6': '६', '7': '७', '8': '८', '9': '९'},
        "sa_IN": {'0': '०', '1': '१', '2': '२', '3': '३', '4': '४', '5': '५', '6': '६', '7': '७', '8': '८', '9': '९'},
        "ar_SA": {'0': '٠', '1': '١', '2': '٢', '3': '٣', '4': '٤', '5': '٥', '6': '٦', '7': '٧', '8': '٨', '9': '٩'},
        "ml_IN": {'0': '൦', '1': '൧', '2': '൨', '3': '൩', '4': '൪', '5': '൫', '6': '൬', '7': '൭', '8': '൮', '9': '൯'},
        "ta_IN": {'0': '௦', '1': '௧', '2': '௨', '3': '௩', '4': '௪', '5': '௫', '6': '௬', '7': '௭', '8': '௮', '9': '௯'}
    }
    
    mapping = num_maps.get(selected_language)
    if not mapping:
        return text
        
    for e_num, l_num in mapping.items():
        text = text.replace(e_num, l_num)
    return text


# def _(key):
#     return translations.get(selected_language, translations["English"]).get(key, key)

update_language()
def _dummy_for_translations_all():
    """This function prevents pybabel from marking dictionary strings as obsolete."""
    _("14 question types")
    _("A saved session was found. Do you want to resume?")
    _("About")
    _("Accuracy")
    _("Addition")
    _("Amazing effort")
    _("Answer")
    _("Answer input")
    _("Are you sure you want to exit?")
    _("Auto-skip in %vs")
    _("Back to Home")
    _("Back to Menu")
    _("Back to Operations")
    _("Begin Warmup")
    _("Bellring")
    _("Cancel")
    _("Choose Mode")
    _("Choose an Operation")
    _("Click below to start the quiz")
    _("Continue to Game Mode")
    _("Correct!")
    _("Correct answer is")
    _("Currency")
    _("Distance")
    _("Division")
    _("Easy")
    _("Enter your answer")
    _("Excellent")
    _("Exit Application")
    _("Extra Hard")
    _("Final Skill")
    _("Game mode! Let's go!")
    _("Good")
    _("Great session!")
    _("Great session! You really know your {strength}. {weakness}")
    _("Hard")
    _("Help")
    _("Invalid — try again")
    _("Keep exploring")
    _("Keep exploring {skill}!")
    _("Keep going!")
    _("Level")
    _("Level: {level}")
    _("Medium")
    _("Missed")
    _("Multiplication")
    _("Next: {level}")
    _("No")
    _("Not Bad")
    _("OK")
    _("Okay")
    _("One more!")
    _("Operations")
    _("Percentage")
    _("Play Again")
    _("Play again?")
    _("Please enter a valid number.")
    _("Proceed to the Game Mode difficulty selector.")
    _("Question")
    _("Question {n} / {total}")
    _("Questions")
    _("Ranked results")
    _("Ready for a new challenge!")
    _("Remainder")
    _("Reset Language")
    _("Resume Session")
    _("Resuming at {lbl_name}")
    _("Same level again — you're getting closer!")
    _("Select Difficulty:")
    _("Select Game Difficulty")
    _("Session Complete")
    _("Session Complete!")
    _("Settings")
    _("Skip")
    _("Skip the current question. Skipped questions score zero.")
    _("Skip this question")
    _("Skipped")
    _("Slow")
    _("Speed matters")
    _("Start Game")
    _("Start Game Mode")
    _("Start Quiz")
    _("Start the warmup match. You will answer 13 questions.")
    _("Starting fresh")
    _("Story")
    _("Submit")
    _("Submit answer")
    _("Subtraction")
    _("Time")
    _("Time out — auto-skipped")
    _("Time's up!")
    _("Time's up! Amazing effort.")
    _("Try Again.")
    _("Type your answer")
    _("Type your answer as a number and press Enter.")
    _("Unknown")
    _("Upload")
    _("Very Fast")
    _("Very Good")
    _("Warmup Complete!")
    _("Warmup Match")
    _("Warmup Match Introduction")
    _("Warmup Question")
    _("Warmup completed early skipped")
    _("Warmup completed early wrong")
    _("Warmup completed success")
    _("Wow!")
    _("Wow! {strength} is your superpower. {weakness}")
    _("Wrong — moving on")
    _("Yes")
    _("You are brilliant across everything!")
    _("You really know your")
    _("You were amazing at")
    _("You were amazing at {strength} today! {weakness}")
    _("and")
    _("cancel")
    _("continue")
    _("is your next adventure!")
    _("is your superpower.")
    _("next adventure")
    _("ready")
    _("remember")
    _("select_language")
    _("superpower")
    _("today!")
    _("trying hard")
    _("very strong")
    _("wants more of your attention next time!")
    _("welcome")
    _("you is getting there!")
    _("you're getting there")
    _("{skill} is your next adventure!")
    _("{skill} wants more of your attention!")
    _("⚡Quickplay")
    _("🎓 Learning Mode")
    _("🎮 Game Mode")

# Extra Game Mode specific strings for pybabel protection
def _dummy_game_mode():
    _("Very Fast")
    _("Good")
    _("Slow")
    _("Missed")
    _("Wrong")
    _("Wrong — moving on")
    _("Invalid — try again")
    _("Skipped")
    _("Time out — auto-skipped")
    _("Correct!")
    _("Warmup Match")
    _("Warmup Complete!")
    _("Continue to Game Mode")
    _("Start Game")
    _("Starting fresh")
    _("Submit")
    _("Skip this question")
    _("Auto-skip in %vs")
    _("Warmup completed early wrong")
    _("Warmup completed success")

# Extra Operator strings for pybabel protection
def _dummy_operators():
    _("plus")
    _("minus")
    _("times")
    _("divided by")
