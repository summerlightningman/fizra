import os

STUDENT_GRADES = (
    "б/р",
    "III(ю)",
    "II(ю)",
    "I(ю)",
    "III",
    "II",
    "I",
    "КМС",
    "МС",
    "МСМК"
)

JUDGE_GRADES = ('ССВК', 'СС1К', 'СС2К')

GENDERS = ('Мужской', 'Женский')

USER_PATTERN = r'(\w+)\s*(\w*\s*)\s*(\w*\s*)'

DOCUMENTS_PATH = os.path.join(os.path.abspath(os.curdir), 'documents')

PROTOCOLS = (
    'Бег 60м',
    'Бег 400м',
    'Бег 800м',
    'Бег 1500м',
    'Бег 3000м',
    'Эстафета 4х400м',
    'Бег 60м с/б',
    'Прыжок в высоту',
    'Прыжок с шестом',
    'Прыжок в длину',
    'Тройной прыжок',
    'Толкание ядра'
)
