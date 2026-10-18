"""Question banks for /quiz and /dailyquestion.

Format: {"id": unique int, "question": str, "options": [2-5 strings (max 80 chars)],
         "answer": index of the correct option in "options"}
Ids only need to be unique inside their own list. Never reuse an id of a quiz
question that was already played, or players will see it as already answered.
This is a starter set - add your own questions below.
"""

QUIZ_QUESTIONS = [
    {"id": 1, "question": "What is the name of Ichigo's Zanpakuto?",
     "options": ["Zangetsu", "Senbonzakura", "Hyorinmaru", "Zabimaru"], "answer": 0},
    {"id": 2, "question": "What is the name of Aizen's Zanpakuto?",
     "options": ["Shinso", "Kyoka Suigetsu", "Suzumushi", "Ryujin Jakka"], "answer": 1},
    {"id": 3, "question": "Which Espada number is Ulquiorra Cifer?",
     "options": ["2nd", "3rd", "4th", "6th"], "answer": 2},
    {"id": 4, "question": "Which Espada number is Grimmjow Jaegerjaquez?",
     "options": ["5th", "6th", "7th", "8th"], "answer": 1},
    {"id": 5, "question": "Who is the Captain-Commander of the Gotei 13?",
     "options": ["Shunsui Kyoraku", "Jushiro Ukitake", "Genryusai Yamamoto", "Sosuke Aizen"], "answer": 2},
    {"id": 6, "question": "Who is the captain of the 10th Division?",
     "options": ["Toshiro Hitsugaya", "Byakuya Kuchiki", "Kenpachi Zaraki", "Mayuri Kurotsuchi"], "answer": 0},
    {"id": 7, "question": "Soi Fon is the captain of which division?",
     "options": ["1st", "2nd", "6th", "12th"], "answer": 1},
    {"id": 8, "question": "What is the name of Byakuya Kuchiki's Zanpakuto?",
     "options": ["Senbonzakura", "Sode no Shirayuki", "Hyorinmaru", "Tobiume"], "answer": 0},
    {"id": 9, "question": "What is the name of Ichigo's father?",
     "options": ["Ryuken", "Isshin", "Kisuke", "Jushiro"], "answer": 1},
    {"id": 10, "question": "Which Espada number is Nelliel Tu Odelschwanck?",
     "options": ["1st", "3rd", "5th", "10th"], "answer": 1},
]

DAILY_QUESTIONS = [
    {"id": 1, "question": "What is the name of Toshiro Hitsugaya's Zanpakuto?",
     "options": ["Hyorinmaru", "Zangetsu", "Kyoka Suigetsu", "Haineko"], "answer": 0},
    {"id": 2, "question": "What is the name of Renji Abarai's Zanpakuto?",
     "options": ["Zabimaru", "Senbonzakura", "Wabisuke", "Benihime"], "answer": 0},
    {"id": 3, "question": "Kenpachi Zaraki is the captain of which division?",
     "options": ["5th", "9th", "11th", "13th"], "answer": 2},
    {"id": 4, "question": "What is the name of Gin Ichimaru's Zanpakuto?",
     "options": ["Suzumushi", "Shinso", "Kyoka Suigetsu", "Tobiume"], "answer": 1},
    {"id": 5, "question": "Which Espada number is Coyote Starrk?",
     "options": ["1st", "2nd", "4th", "10th"], "answer": 0},
    {"id": 6, "question": "What is the name of Rukia Kuchiki's Zanpakuto?",
     "options": ["Sode no Shirayuki", "Ryujin Jakka", "Katen Kyokotsu", "Sogyo no Kotowari"], "answer": 0},
    {"id": 7, "question": "What is the name of Kaname Tosen's Zanpakuto?",
     "options": ["Suzumushi", "Shinso", "Haineko", "Gonryomaru"], "answer": 0},
]
