"""Seed course content: "English for Punjabi speakers".

Each skill is defined by a small vocabulary (english, punjabi) and a few sentences
(punjabi, english, word-to-blank[, alternative english answers]). seed.py expands
these into varied lessons, so the content stays easy to read and extend.
"""

COURSE = {"title": "English", "from_language": "Punjabi", "to_language": "English"}

UNITS = [
    {
        "title": "Basics", "description": "ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ ਕਹਿਣਾ ਤੇ ਆਪਣੀ ਜਾਣ-ਪਛਾਣ ਦੇਣਾ", "color": "#58cc02",
        "skills": [
            {
                "title": "Greetings", "icon": "👋",
                "words": [("hello", "ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ"), ("goodbye", "ਅਲਵਿਦਾ"), ("please", "ਕਿਰਪਾ ਕਰਕੇ"), ("thank you", "ਧੰਨਵਾਦ"),
                          ("sorry", "ਮਾਫ਼ ਕਰਨਾ"), ("yes", "ਹਾਂ"), ("no", "ਨਹੀਂ"), ("welcome", "ਜੀ ਆਇਆਂ ਨੂੰ")],
                "sentences": [
                    ("ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ, ਤੁਸੀਂ ਕਿਵੇਂ ਹੋ?", "Hello, how are you?", "how"),
                    ("ਮੈਂ ਠੀਕ ਹਾਂ, ਧੰਨਵਾਦ।", "I am fine, thank you.", "fine"),
                    ("ਸ਼ੁਭ ਸਵੇਰ!", "Good morning!", "morning"),
                    ("ਤੁਹਾਡਾ ਸੁਆਗਤ ਹੈ।", "You are welcome.", "welcome"),
                    ("ਕਿਰਪਾ ਕਰਕੇ ਬੈਠੋ।", "Please sit down.", "sit"),
                    ("ਅਲਵਿਦਾ, ਕੱਲ੍ਹ ਮਿਲਦੇ ਹਾਂ।", "Goodbye, see you tomorrow.", "tomorrow"),
                ],
            },
            {
                "title": "Introductions", "icon": "🙋",
                "words": [("I", "ਮੈਂ"), ("you", "ਤੁਸੀਂ"), ("name", "ਨਾਮ"), ("my", "ਮੇਰਾ"), ("your", "ਤੁਹਾਡਾ"),
                          ("friend", "ਦੋਸਤ"), ("student", "ਵਿਦਿਆਰਥੀ"), ("teacher", "ਅਧਿਆਪਕ")],
                "sentences": [
                    ("ਮੇਰਾ ਨਾਮ ਸਿਮਰਨ ਹੈ।", "My name is Simran.", "name"),
                    ("ਤੁਹਾਡਾ ਨਾਮ ਕੀ ਹੈ?", "What is your name?", "your"),
                    ("ਮੈਂ ਇੱਕ ਵਿਦਿਆਰਥੀ ਹਾਂ।", "I am a student.", "student"),
                    ("ਤੁਸੀਂ ਮੇਰੇ ਦੋਸਤ ਹੋ।", "You are my friend.", "friend"),
                    ("ਉਹ ਮੇਰੀ ਅਧਿਆਪਕਾ ਹੈ।", "She is my teacher.", "teacher"),
                    ("ਮੈਂ ਪੰਜਾਬ ਤੋਂ ਹਾਂ।", "I am from Punjab.", "Punjab"),
                ],
            },
        ],
    },
    {
        "title": "Food & Family", "description": "ਖਾਣਾ-ਪੀਣਾ ਤੇ ਪਰਿਵਾਰ", "color": "#1cb0f6",
        "skills": [
            {
                "title": "Food", "icon": "🍎",
                "words": [("apple", "ਸੇਬ"), ("bread", "ਰੋਟੀ"), ("rice", "ਚੌਲ"), ("water", "ਪਾਣੀ"),
                          ("milk", "ਦੁੱਧ"), ("tea", "ਚਾਹ"), ("egg", "ਆਂਡਾ"), ("banana", "ਕੇਲਾ")],
                "sentences": [
                    ("ਮੈਨੂੰ ਸੇਬ ਪਸੰਦ ਹਨ।", "I like apples.", "apples", ["I like apple.", "I like the apple."]),
                    ("ਮੈਂ ਪਾਣੀ ਪੀਂਦਾ ਹਾਂ।", "I drink water.", "water"),
                    ("ਉਹ ਚਾਹ ਪੀਂਦੀ ਹੈ।", "She drinks tea.", "tea", ["He drinks tea."]),
                    ("ਅਸੀਂ ਰੋਟੀ ਖਾਂਦੇ ਹਾਂ।", "We eat bread.", "bread"),
                    ("ਮੈਨੂੰ ਦੁੱਧ ਚਾਹੀਦਾ ਹੈ।", "I need milk.", "milk"),
                    ("ਕੀ ਤੁਹਾਨੂੰ ਚੌਲ ਪਸੰਦ ਹਨ?", "Do you like rice?", "rice"),
                ],
            },
            {
                "title": "Family", "icon": "👪",
                "words": [("mother", "ਮਾਂ"), ("father", "ਪਿਤਾ"), ("brother", "ਭਰਾ"), ("sister", "ਭੈਣ"),
                          ("son", "ਪੁੱਤਰ"), ("daughter", "ਧੀ"), ("grandmother", "ਦਾਦੀ"), ("grandfather", "ਦਾਦਾ")],
                "sentences": [
                    ("ਮੇਰੀ ਮਾਂ ਘਰ ਹੈ।", "My mother is at home.", "mother"),
                    ("ਮੇਰੇ ਪਿਤਾ ਜੀ ਡਾਕਟਰ ਹਨ।", "My father is a doctor.", "doctor"),
                    ("ਮੇਰਾ ਇੱਕ ਭਰਾ ਹੈ।", "I have one brother.", "brother", ["I have a brother."]),
                    ("ਉਸਦੀ ਭੈਣ ਸਕੂਲ ਜਾਂਦੀ ਹੈ।", "His sister goes to school.", "sister", ["Her sister goes to school."]),
                    ("ਮੇਰੀ ਦਾਦੀ ਕਹਾਣੀਆਂ ਸੁਣਾਉਂਦੀ ਹੈ।", "My grandmother tells stories.", "grandmother"),
                    ("ਇਹ ਮੇਰਾ ਪਰਿਵਾਰ ਹੈ।", "This is my family.", "family"),
                ],
            },
        ],
    },
    {
        "title": "Daily Life", "description": "ਘਰ, ਸਫ਼ਰ ਤੇ ਸਮਾਂ", "color": "#ce82ff",
        "skills": [
            {
                "title": "Home", "icon": "🏠",
                "words": [("house", "ਘਰ"), ("door", "ਦਰਵਾਜ਼ਾ"), ("window", "ਖਿੜਕੀ"), ("table", "ਮੇਜ਼"),
                          ("chair", "ਕੁਰਸੀ"), ("bed", "ਬਿਸਤਰਾ"), ("kitchen", "ਰਸੋਈ"), ("room", "ਕਮਰਾ")],
                "sentences": [
                    ("ਇਹ ਮੇਰਾ ਘਰ ਹੈ।", "This is my house.", "house", ["This is my home."]),
                    ("ਦਰਵਾਜ਼ਾ ਖੋਲ੍ਹੋ।", "Open the door.", "door"),
                    ("ਮੇਜ਼ ਉੱਤੇ ਕਿਤਾਬ ਹੈ।", "There is a book on the table.", "table"),
                    ("ਕਮਰਾ ਵੱਡਾ ਹੈ।", "The room is big.", "big"),
                    ("ਮਾਂ ਰਸੋਈ ਵਿੱਚ ਹੈ।", "Mother is in the kitchen.", "kitchen", ["My mother is in the kitchen."]),
                    ("ਖਿੜਕੀ ਬੰਦ ਹੈ।", "The window is closed.", "closed"),
                ],
            },
            {
                "title": "Travel", "icon": "🚌",
                "words": [("bus", "ਬੱਸ"), ("train", "ਰੇਲਗੱਡੀ"), ("road", "ਸੜਕ"), ("market", "ਬਾਜ਼ਾਰ"),
                          ("school", "ਸਕੂਲ"), ("hospital", "ਹਸਪਤਾਲ"), ("station", "ਸਟੇਸ਼ਨ"), ("ticket", "ਟਿਕਟ")],
                "sentences": [
                    ("ਮੈਂ ਬਾਜ਼ਾਰ ਜਾ ਰਿਹਾ ਹਾਂ।", "I am going to the market.", "market"),
                    ("ਬੱਸ ਕਿੱਥੇ ਹੈ?", "Where is the bus?", "Where"),
                    ("ਮੈਨੂੰ ਇੱਕ ਟਿਕਟ ਚਾਹੀਦੀ ਹੈ।", "I need a ticket.", "ticket"),
                    ("ਸਟੇਸ਼ਨ ਨੇੜੇ ਹੈ।", "The station is nearby.", "nearby"),
                    ("ਉਹ ਹਸਪਤਾਲ ਵਿੱਚ ਹੈ।", "He is in the hospital.", "hospital", ["She is in the hospital."]),
                    ("ਰੇਲਗੱਡੀ ਦੇਰ ਨਾਲ ਆਈ।", "The train came late.", "late"),
                ],
            },
            {
                "title": "Time", "icon": "⏰",
                "words": [("today", "ਅੱਜ"), ("morning", "ਸਵੇਰ"), ("evening", "ਸ਼ਾਮ"), ("night", "ਰਾਤ"),
                          ("Monday", "ਸੋਮਵਾਰ"), ("Sunday", "ਐਤਵਾਰ"), ("week", "ਹਫ਼ਤਾ"), ("time", "ਸਮਾਂ")],
                "sentences": [
                    ("ਅੱਜ ਸੋਮਵਾਰ ਹੈ।", "Today is Monday.", "Monday"),
                    ("ਮੈਂ ਸਵੇਰੇ ਉੱਠਦਾ ਹਾਂ।", "I wake up in the morning.", "morning", ["I get up in the morning."]),
                    ("ਸ਼ਾਮ ਨੂੰ ਅਸੀਂ ਚਾਹ ਪੀਂਦੇ ਹਾਂ।", "We drink tea in the evening.", "evening"),
                    ("ਰਾਤ ਨੂੰ ਮੈਂ ਸੌਂਦਾ ਹਾਂ।", "I sleep at night.", "night"),
                    ("ਐਤਵਾਰ ਨੂੰ ਛੁੱਟੀ ਹੈ।", "There is a holiday on Sunday.", "Sunday"),
                    ("ਹੁਣ ਕੀ ਸਮਾਂ ਹੋਇਆ ਹੈ?", "What time is it now?", "time"),
                ],
            },
        ],
    },
]

LESSONS_PER_SKILL = 3

ACHIEVEMENTS = [
    # code, title, description, icon, metric, threshold, gem reward
    ("first_steps", "First Steps", "Complete your first lesson", "🌱", "lessons_completed", 1, 10),
    ("on_fire", "On Fire", "Reach a 3 day streak", "🔥", "streak", 3, 15),
    ("week_warrior", "Week Warrior", "Reach a 7 day streak", "⚔️", "streak", 7, 30),
    ("xp_hunter", "XP Hunter", "Earn 100 XP", "⚡", "total_xp", 100, 15),
    ("xp_master", "XP Master", "Earn 500 XP", "🏅", "total_xp", 500, 40),
    ("perfectionist", "Perfectionist", "Finish a lesson with no mistakes", "💎", "perfect_lessons", 1, 15),
    ("skill_master", "Skill Master", "Complete every lesson of a skill", "🎓", "skills_completed", 1, 20),
    ("goal_getter", "Goal Getter", "Hit your daily XP goal", "🎯", "goal_days", 1, 10),
    ("speedster", "Speedster", "Answer 10 questions correctly in a timed practice", "⏱️", "best_timed_correct", 10, 25),
    ("legend", "Legend", "Complete a legendary challenge", "👑", "legendary_count", 1, 50),
]

# name, display name, avatar colour, weekly xp  (leaderboard rivals)
RIVALS = [
    ("gurpreet", "Gurpreet Singh", "#ff9600", 410), ("harleen", "Harleen Kaur", "#ce82ff", 380),
    ("jaspreet", "Jaspreet Sandhu", "#1cb0f6", 355), ("simran", "Simran Gill", "#ff4b4b", 320),
    ("arshdeep", "Arshdeep Brar", "#58cc02", 290), ("manpreet", "Manpreet Dhillon", "#ffc800", 265),
    ("navjot", "Navjot Sidhu", "#1cb0f6", 240), ("kirandeep", "Kirandeep Sekhon", "#ce82ff", 215),
    ("amrit", "Amrit Bajwa", "#ff9600", 180), ("parminder", "Parminder Grewal", "#58cc02", 150),
    ("jasleen", "Jasleen Randhawa", "#ff4b4b", 85), ("tejinder", "Tejinder Cheema", "#1cb0f6", 60),
    ("rupinder", "Rupinder Virk", "#ffc800", 40), ("sukhman", "Sukhman Johal", "#ce82ff", 25),
]
