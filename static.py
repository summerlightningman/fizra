import os

GRADES = (
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

GENDERS = ('Мужской', 'Женский')

DATE_PATTERN = r'(\d?\d)[.;\s:-_/](\d?\d)[.;\s:-_/](\d?\d?\d\d)'

DOCUMENTS_PATH = os.path.join(os.path.abspath(os.curdir), 'documents')
