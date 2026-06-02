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

translations = {   'English': {   'About': 'About',
                   'Addition': 'Addition',
                   'Amazing effort': 'Amazing '
                                     'effort',
                   'Answer': 'Answer',
                   'Answer input': 'Answer '
                                   'input',
                   'Are you sure you want to exit?': 'Are '
                                                     'you '
                                                     'sure '
                                                     'you '
                                                     'want '
                                                     'to '
                                                     'exit?',
                   'Back to Home': 'Back '
                                   'to '
                                   'Home',
                   'Back to Menu': 'Back '
                                   'to '
                                   'Menu',
                   'Back to Operations': 'Back '
                                         'to '
                                         'Operations',
                   'Bellring': 'Bellring',
                   'Choose Mode': 'Choose '
                                  'Mode',
                   'Choose an Operation': 'Choose '
                                          'an '
                                          'Operation',
                   'Click below to start the quiz': 'Click '
                                                    'below '
                                                    'to '
                                                    'start '
                                                    'the '
                                                    'quiz',
                   'Currency': 'Currency',
                   'Distance': 'Distance',
                   'Division': 'Division',
                   'Easy': 'Easy',
                   'Enter your answer': 'Enter '
                                        'your '
                                        'answer',
                   'Exit Application': 'Exit '
                                       'Application',
                   'Extra Hard': 'Extra '
                                 'Hard',
                   "Game mode! Let's go!": 'Game '
                                           'mode! '
                                           "Let's "
                                           'go!',
                   'Great session!': 'Great '
                                     'session!',
                   'Great session! You really know your {strength}. {weakness}': 'Great '
                                                                                 'session! '
                                                                                 'You '
                                                                                 'really '
                                                                                 'know '
                                                                                 'your '
                                                                                 '{strength}. '
                                                                                 '{weakness}',
                   'Hard': 'Hard',
                   'Help': 'Help',
                   'Keep exploring': 'Keep '
                                     'exploring',
                   'Keep exploring {skill}!': 'Keep '
                                              'exploring '
                                              '{skill}!',
                   'Keep going!': 'Keep '
                                  'going!',
                   'Level': 'Level',
                   'Level: {level}': 'Level: '
                                     '{level}',
                   'Medium': 'Medium',
                   'Multiplication': 'Multiplication',
                   'Next: {level}': 'Next: '
                                    '{level}',
                   'One more!': 'One '
                                'more!',
                   'Operations': 'Operations',
                   'Percentage': 'Percentage',
                   'Play Again': 'Play '
                                 'Again',
                   'Play again?': 'Play '
                                  'again?',
                   'Please enter a valid number.': 'Please '
                                                   'enter '
                                                   'a '
                                                   'valid '
                                                   'number.',
                   'Question': 'Question',
                   'Question {n} / {total}': 'Question '
                                             '{n} '
                                             '/ '
                                             '{total}',
                   'Ready for a new challenge!': 'Ready '
                                                 'for '
                                                 'a '
                                                 'new '
                                                 'challenge!',
                   'Remainder': 'Remainder',
                   'Reset Language': 'Reset '
                                     'Language',
                   "Same level again — you're getting closer!": 'Same '
                                                                'level '
                                                                'again '
                                                                '— '
                                                                "you're "
                                                                'getting '
                                                                'closer!',
                   'Select Difficulty:': 'Select '
                                         'Difficulty:',
                   'Select Game Difficulty': 'Select '
                                             'Game '
                                             'Difficulty',
                   'Session Complete': 'Session '
                                       'Complete',
                   'Session Complete!': 'Session '
                                        'Complete!',
                   'Settings': 'Settings',
                   'Start Quiz': 'Start '
                                 'Quiz',
                   'Story': 'Story',
                   'Subtraction': 'Subtraction',
                   'Time': 'Time',
                   "Time's up!": "Time's "
                                 'up!',
                   "Time's up! Amazing effort.": "Time's "
                                                 'up! '
                                                 'Amazing '
                                                 'effort.',
                   'Type your answer': 'Type '
                                       'your '
                                       'answer',
                   'Type your answer as a number and press Enter.': 'Type '
                                                                    'your '
                                                                    'answer '
                                                                    'as '
                                                                    'a '
                                                                    'number '
                                                                    'and '
                                                                    'press '
                                                                    'Enter.',
                   'Upload': 'Upload',
                   'Wow!': 'Wow!',
                   'Wow! {strength} is your superpower. {weakness}': 'Wow! '
                                                                     '{strength} '
                                                                     'is '
                                                                     'your '
                                                                     'superpower. '
                                                                     '{weakness}',
                   'You are brilliant across everything!': 'You '
                                                           'are '
                                                           'brilliant '
                                                           'across '
                                                           'everything!',
                   'You really know your': 'You '
                                           'really '
                                           'know '
                                           'your',
                   'You were amazing at': 'You '
                                          'were '
                                          'amazing '
                                          'at',
                   'You were amazing at {strength} today! {weakness}': 'You '
                                                                       'were '
                                                                       'amazing '
                                                                       'at '
                                                                       '{strength} '
                                                                       'today! '
                                                                       '{weakness}',
                   'and': 'and',
                   'cancel': 'Cancel',
                   'continue': 'Continue',
                   'is your next adventure!': 'is '
                                              'your '
                                              'next '
                                              'adventure!',
                   'is your superpower.': 'is '
                                          'your '
                                          'superpower.',
                   'next adventure': 'next '
                                     'adventure',
                   'ready': 'Ready '
                            'to '
                            'learn '
                            'in '
                            '{lang}!',
                   'remember': 'Remember '
                               'my '
                               'selection',
                   'select_language': 'Select '
                                      'your '
                                      'preferred '
                                      'language:',
                   'superpower': 'superpower',
                   'today!': 'today!',
                   'trying hard': 'trying '
                                  'hard',
                   'very strong': 'very '
                                  'strong',
                   'wants more of your attention next time!': 'wants '
                                                              'more '
                                                              'of '
                                                              'your '
                                                              'attention '
                                                              'next '
                                                              'time!',
                   'welcome': 'Welcome '
                              'to '
                              'Maths '
                              'Tutor!',
                   'you is getting there!': 'you '
                                            'is '
                                            'getting '
                                            'there!',
                   "you're getting there": "you're "
                                           'getting '
                                           'there',
                   '{skill} is your next adventure!': '{skill} '
                                                      'is '
                                                      'your '
                                                      'next '
                                                      'adventure!',
                   '{skill} wants more of your attention!': '{skill} '
                                                            'wants '
                                                            'more '
                                                            'of '
                                                            'your '
                                                            'attention!',
                   '⚡Quickplay': '⚡Quickplay',
                   '🎓 Learning Mode': '🎓 '
                                      'Learning '
                                      'Mode',
                   '🎮 Game Mode': '🎮 '
                                  'Game '
                                  'Mode'},
    'عربي': {   'About': 'حول',
                'Addition': 'جمع',
                'Answer': 'إجابة',
                'Answer input': 'إدخال '
                                'الإجابة',
                'Back to Home': 'العودة '
                                'إلى '
                                'الرئيسية',
                'Back to Menu': 'العودة '
                                'إلى '
                                'القائمة',
                'Back to Operations': 'العودة '
                                      'إلى '
                                      'العمليات',
                'Bellring': 'رنين '
                            'الجرس',
                'Choose an Operation': 'اختر '
                                       'عملية '
                                       'رياضية',
                'Currency': 'العملة',
                'Distance': 'المسافة',
                'Division': 'قسمة',
                'Enter your answer': 'أدخل '
                                     'إجابتك',
                'Help': 'مساعدة',
                'Multiplication': 'ضرب',
                'Operations': 'العمليات',
                'Percentage': 'النسبة '
                              'المئوية',
                'Question': 'سؤال',
                'Remainder': 'الباقي',
                'Settings': 'الإعدادات',
                'Story': 'قصة',
                'Subtraction': 'طرح',
                'Time': 'الوقت',
                'Type your answer as a number and press Enter.': 'اكتب '
                                                                 'إجابتك '
                                                                 'كرقم '
                                                                 'واضغط '
                                                                 'Enter.',
                'Upload': 'تحميل',
                'cancel': 'إلغاء',
                'continue': 'متابعة',
                'ready': 'هل '
                         'أنت '
                         'مستعد '
                         'للتعلم '
                         'بـ{lang}؟',
                'remember': 'تذكر '
                            'اختياري',
                'select_language': 'اختر '
                                   'لغتك '
                                   'المفضلة:',
                'welcome': 'مرحبًا '
                           'بك '
                           'في '
                           'معلم '
                           'الرياضيات!'},
    'संस्कृत': {   'About': 'विवरणम्',
                   'Addition': 'योगः',
                   'Answer': 'उत्तरम्',
                   'Answer input': 'उत्तर '
                                   'निवेशः',
                   'Back to Home': 'मुखपृष्ठं '
                                   'प्रत्यागच्छ',
                   'Back to Menu': 'मेनू '
                                   'प्रत्यागच्छ',
                   'Back to Operations': 'गणितक्रियाः '
                                         'प्रत्यागच्छ',
                   'Bellring': 'घण्टानिनादः',
                   'Choose an Operation': 'एकां '
                                          'गणितक्रियाम् '
                                          'चयनयतु',
                   'Currency': 'मुद्रा',
                   'Distance': 'दूरी',
                   'Division': 'विभाजनम्',
                   'Enter your answer': 'स्वउत्तरं '
                                        'प्रविश्यताम्',
                   'Help': 'साहाय्यम्',
                   'Multiplication': 'गुणनम्',
                   'Operations': 'गणितक्रियाः',
                   'Percentage': 'प्रतिशतः',
                   'Question': 'प्रश्नः',
                   'Remainder': 'शेषः',
                   'Settings': 'संयोजनानि',
                   'Story': 'कथा',
                   'Subtraction': 'वियोगः',
                   'Time': 'समयः',
                   'Type your answer as a number and press Enter.': 'स्वउत्तरं '
                                                                    'संख्यारूपेण '
                                                                    'टङ्कयतु '
                                                                    'Enter '
                                                                    'च '
                                                                    'अमर्त्यतु.',
                   'Upload': 'अधरयतु',
                   'cancel': 'निरसयतु',
                   'continue': 'अनुवर्तस्व',
                   'ready': 'भवान् '
                            '{lang} '
                            'भाषायां '
                            'अध्ययनाय '
                            'सज्जः '
                            'अस्ति '
                            'वा?',
                   'remember': 'मम '
                               'विकल्पं '
                               'स्मर',
                   'select_language': 'भवतः '
                                      'प्रियतमा '
                                      'भाषा '
                                      'चयनयतु:',
                   'welcome': 'गणितशिक्षके '
                              'स्वागतम्!'},
    'हिंदी': {   'About': 'परिचय',
                 'Addition': 'जोड़',
                 'Amazing effort': 'अद्भुत '
                                   'प्रयास',
                 'Answer': 'उत्तर',
                 'Answer input': 'उत्तर '
                                 'इनपुट',
                 'Are you sure you want to exit?': 'क्या '
                                                   'आप '
                                                   'वाकई '
                                                   'बाहर '
                                                   'निकलना '
                                                   'चाहते '
                                                   'हैं?',
                 'Back to Home': 'मुखपृष्ठ '
                                 'पर '
                                 'वापस '
                                 'जाएं',
                 'Back to Menu': 'मेनू '
                                 'पर '
                                 'वापस '
                                 'जाएं',
                 'Back to Operations': 'ऑपरेशन्स '
                                       'पर '
                                       'वापस '
                                       'जाएं',
                 'Bellring': 'घंटी',
                 'Cancel': 'रद्द '
                           'करें',
                 'Choose Mode': 'मोड '
                                'चुनें',
                 'Choose an Operation': 'एक '
                                        'गणितीय '
                                        'क्रिया '
                                        'चुनें',
                 'Click below to start the quiz': 'क्विज़ '
                                                  'शुरू '
                                                  'करने '
                                                  'के '
                                                  'लिए '
                                                  'नीचे '
                                                  'क्लिक '
                                                  'करें',
                 'Correct!': 'सही!',
                 'Currency': 'मुद्रा',
                 'Distance': 'दूरी',
                 'Division': 'भाग',
                 'Easy': 'आसान',
                 'Enter your answer': 'अपना '
                                      'उत्तर '
                                      'दर्ज '
                                      'करें',
                 'Excellent': 'बहुत '
                              'बढ़िया',
                 'Exit Application': 'एप्लिकेशन '
                                     'बंद '
                                     'करें',
                 'Extra Hard': 'बहुत '
                               'कठिन',
                 "Game mode! Let's go!": 'गेम '
                                         'मोड! '
                                         'चलिए '
                                         'शुरू '
                                         'करते '
                                         'हैं!',
                 'Good': 'अच्छा',
                 'Great session!': 'शानदार '
                                   'सत्र!',
                 'Great session! You really know your {strength}. {weakness}': 'शानदार '
                                                                               'सत्र! '
                                                                               'आप '
                                                                               'वास्तव '
                                                                               'में '
                                                                               'अपने '
                                                                               '{strength} '
                                                                               'को '
                                                                               'जानते '
                                                                               'हैं। '
                                                                               '{weakness}',
                 'Hard': 'कठिन',
                 'Help': 'मदद',
                 'Keep exploring': 'अन्वेषण '
                                   'जारी '
                                   'रखें',
                 'Keep exploring {skill}!': '{skill} '
                                            'को '
                                            'एक्सप्लोर '
                                            'करते '
                                            'रहें!',
                 'Keep going!': 'जारी '
                                'रखें!',
                 'Level': 'स्तर',
                 'Medium': 'मध्यम',
                 'Multiplication': 'गुणा',
                 'No': 'नहीं',
                 'Not Bad': 'बुरा '
                            'नहीं',
                 'OK': 'ठीक '
                       'है',
                 'Okay': 'ठीक '
                         'है',
                 'One more!': 'एक '
                              'और!',
                 'Operations': 'गणित '
                               'क्रियाएँ',
                 'Percentage': 'प्रतिशत',
                 'Play Again': 'फिर '
                               'से '
                               'खेलें',
                 'Play again?': 'फिर '
                                'से '
                                'खेलें?',
                 'Please enter a valid number.': 'कृपया '
                                                 'एक '
                                                 'मान्य '
                                                 'संख्या '
                                                 'दर्ज '
                                                 'करें।',
                 'Question': 'प्रश्न',
                 'Ready for a new challenge!': 'एक '
                                               'नई '
                                               'चुनौती '
                                               'के '
                                               'लिए '
                                               'तैयार!',
                 'Remainder': 'शेषफल',
                 'Reset Language': 'भाषा '
                                   'रीसेट '
                                   'करें',
                 "Same level again — you're getting closer!": 'वही '
                                                              'स्तर '
                                                              'फिर '
                                                              'से '
                                                              '— '
                                                              'आप '
                                                              'करीब '
                                                              'आ '
                                                              'रहे '
                                                              'हैं!',
                 'Select Difficulty:': 'कठिनाई '
                                       'चुनें:',
                 'Select Game Difficulty': 'गेम '
                                           'की '
                                           'कठिनाई '
                                           'चुनें',
                 'Session Complete': 'सत्र '
                                     'पूरा '
                                     'हुआ',
                 'Session Complete!': 'सत्र '
                                      'पूरा '
                                      'हुआ!',
                 'Settings': 'सेटिंग्स',
                 'Start Quiz': 'क्विज़ '
                               'शुरू '
                               'करें',
                 'Story': 'कहानी',
                 'Subtraction': 'घटाव',
                 'Time': 'समय',
                 "Time's up!": 'समय '
                               'समाप्त!',
                 "Time's up! Amazing effort.": 'समय '
                                               'समाप्त! '
                                               'अद्भुत '
                                               'प्रयास।',
                 'Try Again.': 'फिर '
                               'से '
                               'प्रयास '
                               'करें।',
                 'Type your answer': 'अपना '
                                     'उत्तर '
                                     'टाइप '
                                     'करें',
                 'Type your answer as a number and press Enter.': 'अपना '
                                                                  'उत्तर '
                                                                  'एक '
                                                                  'संख्या '
                                                                  'के '
                                                                  'रूप '
                                                                  'में '
                                                                  'टाइप '
                                                                  'करें '
                                                                  'और '
                                                                  'Enter '
                                                                  'दबाएं।',
                 'Upload': 'अपलोड '
                           'करें',
                 'Very Good': 'बहुत '
                              'अच्छा',
                 'Wow!': 'वाह!',
                 'Wow! {strength} is your superpower. {weakness}': 'वाह! '
                                                                   '{strength} '
                                                                   'आपकी '
                                                                   'महाशक्ति '
                                                                   'है। '
                                                                   '{weakness}',
                 'Yes': 'हाँ',
                 'You are brilliant across everything!': 'आप '
                                                         'हर '
                                                         'चीज '
                                                         'में '
                                                         'शानदार '
                                                         'हैं!',
                 'You really know your': 'आप '
                                         'वास्तव '
                                         'में '
                                         'जानते '
                                         'हैं',
                 'You were amazing at': 'आप '
                                        'कमाल '
                                        'थे',
                 'You were amazing at {strength} today! {weakness}': 'आज '
                                                                     'आप '
                                                                     '{strength} '
                                                                     'में '
                                                                     'कमाल '
                                                                     'थे! '
                                                                     '{weakness}',
                 'and': 'और',
                 'cancel': 'रद्द '
                           'करें',
                 'continue': 'जारी '
                             'रखें',
                 'is your next adventure!': 'आपका '
                                            'अगला '
                                            'साहसिक '
                                            'कार्य '
                                            'है!',
                 'is your superpower.': 'आपकी '
                                        'महाशक्ति '
                                        'है।',
                 'next adventure': 'अगला '
                                   'साहसिक '
                                   'कार्य',
                 'ready': '{lang} '
                          'में '
                          'सीखने '
                          'के '
                          'लिए '
                          'तैयार '
                          'हैं?',
                 'remember': 'मेरी '
                             'पसंद '
                             'याद '
                             'रखें',
                 'select_language': 'अपनी '
                                    'पसंदीदा '
                                    'भाषा '
                                    'चुनें:',
                 'superpower': 'महाशक्ति',
                 'today!': 'आज!',
                 'trying hard': 'कड़ी '
                                'मेहनत',
                 'very strong': 'बहुत '
                                'मजबूत',
                 'wants more of your attention next time!': 'अगली '
                                                            'बार '
                                                            'अधिक '
                                                            'ध्यान '
                                                            'देने '
                                                            'की '
                                                            'आवश्यकता '
                                                            'है!',
                 'welcome': 'मैथ्स '
                            'ट्यूटर '
                            'में '
                            'आपका '
                            'स्वागत '
                            'है!',
                 'you is getting there!': 'आप '
                                          'पहुँच '
                                          'रहे '
                                          'हैं!',
                 "you're getting there": 'आप '
                                         'पहुँच '
                                         'रहे '
                                         'हैं',
                 '{skill} is your next adventure!': '{skill} '
                                                    'आपका '
                                                    'अगला '
                                                    'साहसिक '
                                                    'कार्य '
                                                    'है!',
                 '{skill} wants more of your attention!': '{skill} '
                                                          'को '
                                                          'आपके '
                                                          'अधिक '
                                                          'ध्यान '
                                                          'की '
                                                          'आवश्यकता '
                                                          'है!',
                 '⚡Quickplay': '⚡त्वरित '
                               'खेल',
                 '🎓 Learning Mode': '🎓 '
                                    'सीखने '
                                    'का '
                                    'मोड',
                 '🎮 Game Mode': '🎮 '
                                'गेम '
                                'मोड'},
    'தமிழ்': {   'About': 'பற்றி',
                 'Addition': 'கூட்டல்',
                 'Answer': 'பதில்',
                 'Answer input': 'பதில் '
                                 'உள்ளீடு',
                 'Back to Home': 'முகப்புக்கு '
                                 'திரும்பு',
                 'Back to Menu': 'மெனுவுக்கு '
                                 'திரும்பு',
                 'Back to Operations': 'செயல்பாடுகளுக்கு '
                                       'திரும்பு',
                 'Bellring': 'மணியழுத்தம்',
                 'Choose an Operation': 'ஒரு '
                                        'கணிதச் '
                                        'செயலைத் '
                                        'தேர்ந்தெடுக்கவும்',
                 'Currency': 'நாணயம்',
                 'Distance': 'தூரம்',
                 'Division': 'வகுத்தல்',
                 'Enter your answer': 'உங்கள் '
                                      'பதிலை '
                                      'உள்ளிடுங்கள்',
                 'Help': 'உதவி',
                 'Multiplication': 'பெருக்கல்',
                 'Operations': 'கணிதச் '
                               'செயல்கள்',
                 'Percentage': 'சதவீதம்',
                 'Question': 'கேள்வி',
                 'Remainder': 'மீதமுள்ளவை',
                 'Settings': 'அமைப்புகள்',
                 'Story': 'கதை',
                 'Subtraction': 'கழித்தல்',
                 'Time': 'நேரம்',
                 'Type your answer as a number and press Enter.': 'உங்கள் '
                                                                  'பதிலை '
                                                                  'ஒரு '
                                                                  'எண்ணாக '
                                                                  'தட்டச்சு '
                                                                  'செய்து '
                                                                  'Enter '
                                                                  'அமுக்கவும்.',
                 'Upload': 'பதிவேற்று',
                 'cancel': 'ரத்து '
                           'செய்',
                 'continue': 'தொடரவும்',
                 'ready': '{lang} '
                          'மொழியில் '
                          'கற்க '
                          'தயார்?',
                 'remember': 'என் '
                             'தேர்வை '
                             'நினைவில் '
                             'கொள்ளவும்',
                 'select_language': 'விருப்பமான '
                                    'மொழியைத் '
                                    'தேர்ந்தெடுக்கவும்:',
                 'welcome': 'மாத்த்ஸ் '
                            'டூட்டருக்கு '
                            'வரவேற்கிறோம்!'},
    'മലയാളം': {   'About': 'വിവരങ്ങൾ',
                  'Addition': 'സങ്കലനം',
                  'Amazing effort': 'അതിശയകരമായ '
                                    'ശ്രമം',
                  'Answer': 'ഉത്തരം',
                  'Answer input': 'ഉത്തര '
                                  'ഇൻപുട്ട്',
                  'Are you sure you want to exit?': 'നിങ്ങൾ '
                                                    'പുറത്തുകടക്കാൻ '
                                                    'ഉറപ്പാണോ?',
                  'Back to Home': 'തുടക്കത്തിലേക്ക് '
                                  'മടങ്ങുക',
                  'Back to Menu': 'മെനുവിലേക്ക് '
                                  'മടങ്ങുക',
                  'Back to Operations': 'ഓപ്പറേഷനുകളിലേക്ക് '
                                        'മടങ്ങുക',
                  'Bellring': 'ബെൽ '
                              'റിംഗ്',
                  'Cancel': 'റദ്ദാക്കുക',
                  'Choose Mode': 'മോഡ് '
                                 'തിരഞ്ഞെടുക്കുക',
                  'Choose an Operation': 'ഒരു '
                                         'ഗണിത '
                                         'പ്രവർത്തനം '
                                         'തിരഞ്ഞെടുക്കൂ',
                  'Click below to start the quiz': 'ക്വിസ് '
                                                   'ആരംഭിക്കാൻ '
                                                   'താഴെ '
                                                   'ക്ലിക്ക് '
                                                   'ചെയ്യുക',
                  'Correct!': 'ശരിയാണ്!',
                  'Currency': 'കറൻസി',
                  'Distance': 'ദൂരം',
                  'Division': 'ഹരണം',
                  'Easy': 'എളുപ്പം',
                  'Enter your answer': 'നിങ്ങളുടെ '
                                       'ഉത്തരമിടുക',
                  'Excellent': 'മികച്ചത്',
                  'Exit Application': 'പുറത്ത് '
                                      'കടക്കുക',
                  'Extra Hard': 'അതി '
                                'കഠിനം',
                  "Game mode! Let's go!": 'ഗെയിം '
                                          'മോഡ്! '
                                          'നമുക്ക് '
                                          'പോകാം!',
                  'Good': 'നല്ലത്',
                  'Great session!': 'മികച്ച '
                                    'സെഷൻ!',
                  'Great session! You really know your {strength}. {weakness}': 'മികച്ച '
                                                                                'സെഷൻ! '
                                                                                'നിങ്ങൾക്ക് '
                                                                                '{strength} '
                                                                                'ശരിക്കും '
                                                                                'അറിയാം. '
                                                                                '{weakness}',
                  'Hard': 'കഠിനം',
                  'Help': 'സഹായം',
                  'Keep exploring': 'പര്യവേക്ഷണം '
                                    'തുടരുക',
                  'Keep exploring {skill}!': '{skill} '
                                             'പര്യവേക്ഷണം '
                                             'തുടരുക!',
                  'Keep going!': 'തുടരുക!',
                  'Level': 'ലെവൽ',
                  'Medium': 'ഇടത്തരം',
                  'Multiplication': 'ഗുണനം',
                  'No': 'ഇല്ല',
                  'Not Bad': 'മോശമല്ല',
                  'OK': 'ശരി',
                  'Okay': 'ശരി',
                  'One more!': 'ഒരെണ്ണം '
                               'കൂടി!',
                  'Operations': 'ഗണിതക്രിയകൾ',
                  'Percentage': 'ശതമാനം',
                  'Play Again': 'വീണ്ടും '
                                'കളിക്കുക',
                  'Play again?': 'വീണ്ടും '
                                 'കളിക്കണോ?',
                  'Please enter a valid number.': 'ദയവായി '
                                                  'ഒരു '
                                                  'സാധുവായ '
                                                  'നമ്പർ '
                                                  'നൽകുക.',
                  'Question': 'ചോദ്യം',
                  'Ready for a new challenge!': 'ഒരു '
                                                'പുതിയ '
                                                'വെല്ലുവിളിക്ക് '
                                                'തയ്യാറാണ്!',
                  'Remainder': 'ശിഷ്ടം',
                  'Reset Language': 'ഭാഷ '
                                    'പുനഃസജ്ജമാക്കുക',
                  "Same level again — you're getting closer!": 'അതേ '
                                                               'ലെവൽ '
                                                               'വീണ്ടും '
                                                               '— '
                                                               'നിങ്ങൾ '
                                                               'അടുത്തുന്നു!',
                  'Select Difficulty:': 'കാഠിന്യം '
                                        'തിരഞ്ഞെടുക്കുക:',
                  'Select Game Difficulty': 'ഗെയിം '
                                            'കാഠിന്യം '
                                            'തിരഞ്ഞെടുക്കുക',
                  'Session Complete': 'സெഷൻ '
                                      'പൂർത്തിയായി',
                  'Session Complete!': 'സെഷൻ '
                                       'പൂർത്തിയായി!',
                  'Settings': 'ക്രമീകരണങ്ങൾ',
                  'Start Quiz': 'ക്വിസ് '
                                'ആരംഭിക്കുക',
                  'Story': 'കഥ',
                  'Subtraction': 'വ്യവകലനം',
                  'Time': 'സമയം',
                  "Time's up!": 'സമയം '
                                'കഴിഞ്ഞു!',
                  "Time's up! Amazing effort.": 'സമയം '
                                                'കഴിഞ്ഞു! '
                                                'അതിശയകരമായ '
                                                'ശ്രമം.',
                  'Try Again.': 'വീണ്ടും '
                                'ശ്രമിക്കുക',
                  'Type your answer': 'നിങ്ങളുടെ '
                                      'ഉത്തരം '
                                      'ടൈപ്പ് '
                                      'ചെയ്യുക',
                  'Type your answer as a number and press Enter.': 'നിങ്ങളുടെ '
                                                                   'ഉത്തരം '
                                                                   'ഒരു '
                                                                   'നമ്പരായി '
                                                                   'ടൈപ്പ് '
                                                                   'ചെയ്ത് '
                                                                   'Enter '
                                                                   'അമർത്തുക.',
                  'Upload': 'അപ്\u200cലോഡ് '
                            'ചെയ്യുക',
                  'Very Good': 'വളരെ '
                               'നല്ലത്',
                  'Wow!': 'കൊള്ളാം!',
                  'Wow! {strength} is your superpower. {weakness}': 'കൊള്ളാം! '
                                                                    '{strength} '
                                                                    'നിങ്ങളുടെ '
                                                                    'മഹാശക്തിയാണ്. '
                                                                    '{weakness}',
                  'Yes': 'അതെ',
                  'You are brilliant across everything!': 'നിങ്ങൾ '
                                                          'എല്ലാറ്റിലും '
                                                          'മിടുക്കനാണ്!',
                  'You really know your': 'നിങ്ങൾക്ക് '
                                          'ശരിക്കും '
                                          'അറിയാം',
                  'You were amazing at': 'നിങ്ങൾ '
                                         'മികച്ചതായിരുന്നു',
                  'You were amazing at {strength} today! {weakness}': 'നിങ്ങൾ '
                                                                      'ഇന്ന് '
                                                                      '{strength} '
                                                                      'ൽ '
                                                                      'മികച്ചവനായിരുന്നു! '
                                                                      '{weakness}',
                  'and': 'കൂടാതെ',
                  'cancel': 'റദ്ദാക്കുക',
                  'continue': 'തുടരുക',
                  'is your next adventure!': 'നിങ്ങളുടെ '
                                             'അടുത്ത '
                                             'സാഹസികതയാണ്!',
                  'is your superpower.': 'നിങ്ങളുടെ '
                                         'മഹാശക്തിയാണ്.',
                  'next adventure': 'അടുത്ത '
                                    'സാഹസികത',
                  'ready': '{lang} '
                           'ഭാഷയിൽ '
                           'പഠിക്കാൻ '
                           'തയ്യാറാണോ?',
                  'remember': 'എന്റെ '
                              'തിരഞ്ഞെടുപ്പ് '
                              'ഓർക്കുക',
                  'select_language': 'നിങ്ങളുടെ '
                                     'ഇഷ്ടപ്പെട്ട '
                                     'ഭാഷ '
                                     'തിരഞ്ഞെടുക്കുക:',
                  'superpower': 'മഹാശക്തി',
                  'today!': 'ഇന്ന്!',
                  'trying hard': 'കഠിനമായി '
                                 'ശ്രമിക്കുന്നു',
                  'very strong': 'വളരെ '
                                 'ശക്തമായ',
                  'wants more of your attention next time!': 'അടുത്ത '
                                                             'തവണ '
                                                             'നിങ്ങളുടെ '
                                                             'കൂടുതൽ '
                                                             'ശ്രദ്ധ '
                                                             'വേണം!',
                  'welcome': 'മാത്\u200cസ് '
                             'ട്യൂട്ടറിലേക്ക് '
                             'സ്വാഗതം!',
                  'you is getting there!': 'നിങ്ങൾ '
                                           'അവിടെയെത്തുന്നു!',
                  "you're getting there": 'നിങ്ങൾ '
                                          'അവിടെയെത്തുന്നു',
                  '{skill} is your next adventure!': '{skill} '
                                                     'നിങ്ങളുടെ '
                                                     'അടുത്ത '
                                                     'സാഹസികതയാണ്!',
                  '{skill} wants more of your attention!': '{skill} '
                                                           'നിങ്ങളുടെ '
                                                           'കൂടുതൽ '
                                                           'ശ്രദ്ധ '
                                                           'ആവശ്യപ്പെടുന്നു!',
                  '⚡Quickplay': '⚡ക്വിക്ക് '
                                'പ്ലേ',
                  '🎓 Learning Mode': '🎓 '
                                     'പഠന '
                                     'മോഡ്',
                  '🎮 Game Mode': '🎮 ഗെയിം മോഡ്',
                  'Warmup Match': 'വാംഅപ്പ് മത്സരം',
                  'Warmup Match Introduction': 'വാംഅപ്പ് മത്സരം ആമുഖം',
                  'Speed matters': 'വേഗത പ്രധാനമാണ്',
                  '14 question types': '14 ചോദ്യ തരങ്ങൾ',
                  'Ranked results': 'റാങ്ക് ചെയ്ത ഫലങ്ങൾ',
                  'Begin Warmup': 'വാംഅപ്പ് ആരംഭിക്കുക',
                  'Start the warmup match. You will answer 13 questions.': 'വാംഅപ്പ് മത്സരം ആരംഭിക്കുക. നിങ്ങൾ 13 ചോദ്യങ്ങൾക്ക് ഉത്തരം നൽകും.',
                  'Warmup Question': 'വാംഅപ്പ് ചോദ്യം',
                  'Auto-skip in %vs': '%vs സെക്കൻഡിൽ ഓട്ടോ-സ്കിപ്പ് ആകും',
                  'Submit': 'സമർപ്പിക്കുക',
                  'Submit answer': 'ഉത്തരം സമർപ്പിക്കുക',
                  'Skip this question': 'ഈ ചോദ്യം ഒഴിവാക്കുക',
                  'Skip the current question. Skipped questions score zero.': 'നിലവിലെ ചോദ്യം ഒഴിവാക്കുക. ഒഴിവാക്കിയ ചോദ്യങ്ങൾക്ക് പൂജ്യം സ്കോർ ആയിരിക്കും ലഭിക്കുക.',
                  'Invalid — try again': 'തെറ്റായ ഇൻപുട്ട് — വീണ്ടും ശ്രമിക്കുക',
                  'Wrong — moving on': 'തെറ്റാണ് — അടുത്ത ചോദ്യത്തിലേക്ക് പോകുന്നു',
                  'Skipped': 'ഒഴിവാക്കി',
                  'Time out — auto-skipped': 'സമയം കഴിഞ്ഞു — ഓട്ടോ-സ്കിപ്പ് ചെയ്തു',
                  'Warmup Complete!': 'വാംഅപ്പ് പൂർത്തിയായി!',
                  'Continue to Game Mode': 'ഗെയിം മോഡിലേക്ക് തുടരുക',
                  'Proceed to the Game Mode difficulty selector.': 'ഗെയിം മോഡ് കാഠിന്യം തിരഞ്ഞെടുക്കുന്നതിലേക്ക് പോകുക.',
                  'Starting fresh': 'ആദ്യം മുതൽ ആരംഭിക്കുന്നു',
                  'Resuming at {lbl_name}': '{lbl_name} എന്നതിൽ പുനരാരംഭിക്കുന്നു',
                  'Start Game': 'ഗെയിം ആരംഭിക്കുക',
                  'Start Game Mode': 'ഗെയിം മോഡ് ആരംഭിക്കുക',
                  'Skip': 'ഒഴിവാക്കുക',
                  'Warmup completed early wrong': 'നിങ്ങൾ {correct}/{total} ചോദ്യങ്ങൾക്ക് ശരിയായി ഉത്തരം നൽകി. വാംഅപ്പ് നേരത്തെ അവസാനിച്ചു — സാരമില്ല!',
                  'Warmup completed early skipped': 'നിങ്ങൾ {correct}/{total} ചോദ്യങ്ങൾക്ക് ഉത്തരം നൽകി. കൂടുതൽ ചോദ്യങ്ങൾ ഒഴിവാക്കിയതിനാൽ വാംഅപ്പ് അവസാനിച്ചു — സാരമില്ല!',
                  'Warmup completed success': 'എല്ലാ {total} ചോദ്യങ്ങളും പൂർത്തിയാക്കിയതിൽ അഭിനന്ദനങ്ങൾ! നിങ്ങൾക്ക് {correct} ശരിയുത്തരങ്ങൾ ലഭിച്ചു.',
                  'Very Fast': 'വളരെ വേഗതയേറിയത്',
                  'Slow': 'പതുക്കെ',
                  'Missed': 'നഷ്ടമായി',
                  'Unknown': 'അജ്ഞാതം',
                  'Questions': 'ചോദ്യങ്ങൾ',
                  'Accuracy': 'കൃത്യത',
                  'Final Skill': 'അവസാന ഘട്ടം'}}

# Session Resume Translations
translations['English']['A saved session was found. Do you want to resume?'] = 'A saved session was found. Do you want to resume?'
translations['English']['Resume Session'] = 'Resume Session'

translations['عربي']['A saved session was found. Do you want to resume?'] = 'تم العثور على جلسة محفوظة. هل تريد الاستئناف؟'
translations['عربي']['Resume Session'] = 'استئناف الجلسة'

translations['संस्कृत']['A saved session was found. Do you want to resume?'] = 'एकः सुरक्षितः सङ्क्रमഃ प्राप्तः। किं भवान् अनुवर्तितुम् इच्छति?'
translations['संस्कृत']['Resume Session'] = 'सङ्क्रमं अनुवर्तस्व'

translations['हिंदी']['A saved session was found. Do you want to resume?'] = 'एक सहेजा गया सत्र मिला। क्या आप इसे फिर से शुरू करना चाहते हैं?'
translations['हिंदी']['Resume Session'] = 'सत्र फिर से शुरू करें'

translations['தமிழ்']['A saved session was found. Do you want to resume?'] = 'சேமிக்கப்பட்ட அமர்வு கண்டறியப்பட்டது. அதை மீண்டும் தொடங்க விரும்புகிறீர்களா?'
translations['தமிழ்']['Resume Session'] = 'அமர்வை மீண்டும் தொடங்கு'

translations['മലയാളം']['A saved session was found. Do you want to resume?'] = 'ഒരു സേവ് ചെയ്ത സെഷൻ കണ്ടെത്തി. നിങ്ങൾക്ക് ഇത് പുനരാരംഭിക്കണമെന്നുണ്ടോ?'
translations['മലയാളം']['Resume Session'] = 'സെഷൻ പുനരാരംഭിക്കുക'

def tr(key):
    return translations.get(selected_language, translations["English"]).get(key, key)