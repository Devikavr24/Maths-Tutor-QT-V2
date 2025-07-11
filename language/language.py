# language/language.py
import os

selected_language = "English"

CONFIG_FILE = "selected_lang.txt"

def save_selected_language_to_file(lang):
    print("save to file function called")
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        f.write(lang)

def get_saved_language():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    return None

def set_language(lang):
    global selected_language
    selected_language = lang

def clear_remember_language():
    if os.path.exists(CONFIG_FILE):
        os.remove(CONFIG_FILE)

translations = {
    "English": {
        "welcome": "Welcome to Maths Tutor!",
        "ready": "Ready to learn in {lang}!",
        "Story": "Story",
        "Time": "Time",
        "Currency": "Currency",
        "Distance": "Distance",
        "Bellring": "Bellring",
        "Operations": "Operations",
        "Upload": "Upload",
        "Help": "Help",
        "About": "About",
        "Settings": "Settings",
        "Addition": "Addition",
        "Subtraction": "Subtraction",
        "Multiplication": "Multiplication",
        "Division": "Division",
        "Remainder": "Remainder",
        "Percentage": "Percentage",
        "Back to Home": "Back to Home",
        "Back to Operations": "Back to Operations",
        "select_language": "Select your preferred language:",
        "remember": "Remember my selection",
        "continue": "Continue",
        "cancel": "Cancel",
        "Choose an Operation": "Choose an Operation",
        "Enter your answer": "Enter your answer"
    },
    "മലയാളം": {
        "welcome": "മാത്‌സ് ട്യൂട്ടറിലേക്ക് സ്വാഗതം!",
        "ready": "{lang} ഭാഷയിൽ പഠിക്കാൻ തയ്യാറാണോ?",
        "Story": "കഥ",
        "Time": "സമയം",
        "Currency": "കറൻസി",
        "Distance": "ദൂരം",
        "Bellring": "ബെൽ റിംഗ്",
        "Operations": "ഗണിതക്രിയകൾ",
        "Upload": "അപ്‌ലോഡ് ചെയ്യുക",
        "Help": "സഹായം",
        "About": "വിവരങ്ങൾ",
        "Settings": "ക്രമീകരണങ്ങൾ",
        "Addition": "സങ്കലനം",
        "Subtraction": "വ്യവകലനം",
        "Multiplication": "ഗുണനം",
        "Division": "ഹരണം",
        "Remainder": "ശിഷ്ടം",
        "Percentage": "ശതമാനം",
        "Back to Home": "തുടക്കത്തിലേക്ക് മടങ്ങുക",
        "Back to Operations": "ഓപ്പറേഷനുകളിലേക്ക് മടങ്ങുക",
        "select_language": "നിങ്ങളുടെ ഇഷ്ടപ്പെട്ട ഭാഷ തിരഞ്ഞെടുക്കുക:",
        "remember": "എന്റെ തിരഞ്ഞെടുപ്പ് ഓർക്കുക",
        "continue": "തുടരുക",
        "cancel": "റദ്ദാക്കുക",
        "Choose an Operation": "ഒരു ഗണിത പ്രവർത്തനം തിരഞ്ഞെടുക്കൂ",
        "Enter your answer": "നിങ്ങളുടെ ഉത്തരമിടുക"
    },
    "हिंदी": {
        "welcome": "मैथ्स ट्यूटर में आपका स्वागत है!",
        "ready": "{lang} में सीखने के लिए तैयार हैं?",
        "Story": "कहानी",
        "Time": "समय",
        "Currency": "मुद्रा",
        "Distance": "दूरी",
        "Bellring": "घंटी",
        "Operations": "गणित क्रियाएँ",
        "Upload": "अपलोड करें",
        "Help": "मदद",
        "About": "परिचय",
        "Settings": "सेटिंग्स",
        "Addition": "जोड़",
        "Subtraction": "घटाव",
        "Multiplication": "गुणा",
        "Division": "भाग",
        "Remainder": "शेषफल",
        "Percentage": "प्रतिशत",
        "Back to Home": "मुखपृष्ठ पर वापस जाएं",
        "Back to Operations": "ऑपरेशन्स पर वापस जाएं",
        "select_language": "अपनी पसंदीदा भाषा चुनें:",
        "remember": "मेरी पसंद याद रखें",
        "continue": "जारी रखें",
        "cancel": "रद्द करें",
        "Choose an Operation": "एक गणितीय क्रिया चुनें",
        "Enter your answer": "अपना उत्तर दर्ज करें"
    },
    "தமிழ்": {
        "welcome": "மாத்த்ஸ் டூட்டருக்கு வரவேற்கிறோம்!",
        "ready": "{lang} மொழியில் கற்க தயார்吗?",
        "Story": "கதை",
        "Time": "நேரம்",
        "Currency": "நாணயம்",
        "Distance": "தூரம்",
        "Bellring": "மணியழுத்தம்",
        "Operations": "கணிதச் செயல்கள்",
        "Upload": "பதிவேற்று",
        "Help": "உதவி",
        "About": "பற்றி",
        "Settings": "அமைப்புகள்",
        "Addition": "கூட்டல்",
        "Subtraction": "கழித்தல்",
        "Multiplication": "பெருக்கல்",
        "Division": "வகுத்தல்",
        "Remainder": "மீதமுள்ளவை",
        "Percentage": "சதவீதம்",
        "Back to Home": "முகப்புக்கு திரும்பு",
        "Back to Operations": "செயல்பாடுகளுக்கு திரும்பு",
        "select_language": "விருப்பமான மொழியைத் தேர்ந்தெடுக்கவும்:",
        "remember": "என் தேர்வை நினைவில் கொள்ளவும்",
        "continue": "தொடரவும்",
        "cancel": "ரத்து செய்",
        "Choose an Operation": "ஒரு கணிதச் செயலைத் தேர்ந்தெடுக்கவும்",
        "Enter your answer": "உங்கள் பதிலை உள்ளிடுங்கள்"
    },
    "عربي": {
        "welcome": "مرحبًا بك في معلم الرياضيات!",
        "ready": "هل أنت مستعد للتعلم بـ{lang}؟",
        "Story": "قصة",
        "Time": "الوقت",
        "Currency": "العملة",
        "Distance": "المسافة",
        "Bellring": "رنين الجرس",
        "Operations": "العمليات",
        "Upload": "تحميل",
        "Help": "مساعدة",
        "About": "حول",
        "Settings": "الإعدادات",
        "Addition": "جمع",
        "Subtraction": "طرح",
        "Multiplication": "ضرب",
        "Division": "قسمة",
        "Remainder": "الباقي",
        "Percentage": "النسبة المئوية",
        "Back to Home": "العودة إلى الرئيسية",
        "Back to Operations": "العودة إلى العمليات",
        "select_language": "اختر لغتك المفضلة:",
        "remember": "تذكر اختياري",
        "continue": "متابعة",
        "cancel": "إلغاء",
        "Choose an Operation": "اختر عملية رياضية",
        "Enter your answer": "أدخل إجابتك"
    },
    "संस्कृत": {
        "welcome": "गणितशिक्षके स्वागतम्!",
        "ready": "भवान् {lang} भाषायां अध्ययनाय सज्जः अस्ति वा?",
        "Story": "कथा",
        "Time": "समयः",
        "Currency": "मुद्रा",
        "Distance": "दूरी",
        "Bellring": "घण्टानिनादः",
        "Operations": "गणितक्रियाः",
        "Upload": "अधरयतु",
        "Help": "साहाय्यम्",
        "About": "विवरणम्",
        "Settings": "संयोजनानि",
        "Addition": "योगः",
        "Subtraction": "वियोगः",
        "Multiplication": "गुणनम्",
        "Division": "विभाजनम्",
        "Remainder": "शेषः",
        "Percentage": "प्रतिशतः",
        "Back to Home": "मुखपृष्ठं प्रत्यागच्छ",
        "Back to Operations": "गणितक्रियाः प्रत्यागच्छ",
        "select_language": "भवतः प्रियतमा भाषा चयनयतु:",
        "remember": "मम विकल्पं स्मर",
        "continue": "अनुवर्तस्व",
        "cancel": "निरसयतु",
        "Choose an Operation": "एकां गणितक्रियाम् चयनयतु",
        "Enter your answer": "स्वउत्तरं प्रविश्यताम्"
    }
}

def tr(key):
    return translations.get(selected_language, translations["English"]).get(key, key)
