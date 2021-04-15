from PyQt5 import QtWidgets
from window import Window

from units.student_list import StudentList
from units.document_list import DocumentList
from units.team_list import TeamList
from units.judge_list import JudgeList
from units.protocol_list import ProtocolList
from units.category_list import CategoryList
from units.coach_list import CoachList

import os
import sqlite3
from itertools import starmap


class Main(Window):
    def __init__(self):
        super().__init__()
        self.validate_run()

        self.db_connection = sqlite3.connect('data.db')
        self.cur = self.db_connection.cursor()

        tabs = (
            (StudentList(self.db_connection, self.cur),                  'Участники'),
            (CoachList(self.db_connection, self.cur),                      'Тренера'),
            (TeamList(self.db_connection, self.cur),                       'Команды'),
            (CategoryList(self.db_connection, self.cur),                 'Категории'),
            (JudgeList(self.db_connection, self.cur),                        'Судьи'),
            (DocumentList(),                                             'Документы'),
            (ProtocolList(self.db_connection, self.cur),    'Протоколы соревнований')

        )

        self.tab_widget = QtWidgets.QTabWidget()
        tuple(starmap(self.tab_widget.addTab, tabs))

        self.main_layout.addWidget(self.tab_widget)

    def validate_run(self):
        if not os.path.exists('data.db'):
            QtWidgets.QMessageBox.critical(self, 'Ошибка', 'База данных (файл data.db) не найдена!')
            exit(0)


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    window = Main()
    window.setWindowTitle('Физ-ра')
    window.showMaximized()
    sys.exit(app.exec_())
