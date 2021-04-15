import sqlite3
import re

from PyQt5 import QtGui, QtCore, QtWidgets

from window import Window
from widgets.list import List
from widgets.list_item import ListItem
from static import USER_PATTERN


class CoachList(Window):
    def __init__(self, db_connection: sqlite3.Connection, cursor: sqlite3.Cursor):
        super().__init__()

        self.db_connection = db_connection
        self.cur = cursor

        self.search_field = QtWidgets.QLineEdit()
        self.search_field.setPlaceholderText('Поиск по ФИО...')
        self.search_field.returnPressed.connect(self.refresh_list)

        search_layout = QtWidgets.QHBoxLayout()
        search_layout.addWidget(self.search_field)

        search_group = QtWidgets.QGroupBox('Поиск тренера')
        search_group.setLayout(search_layout)

        self.coach_list = List(self)
        self.refresh_list()

        self.new_surname = QtWidgets.QLineEdit()
        self.new_surname.setPlaceholderText('Фамилия')

        self.new_name = QtWidgets.QLineEdit()
        self.new_name.setPlaceholderText('Имя')

        self.new_lastname = QtWidgets.QLineEdit()
        self.new_lastname.setPlaceholderText('Отчество')

        add_button = QtWidgets.QPushButton('Добавить')
        add_button.clicked.connect(self.add)

        new_layout = QtWidgets.QHBoxLayout()
        new_widgets = (self.new_surname, self.new_name, self.new_lastname, add_button)
        tuple(map(new_layout.addWidget, new_widgets))

        new_group = QtWidgets.QGroupBox('Добавить нового тренера')
        new_group.setLayout(new_layout)

        self.main_layout.addWidget(search_group)
        self.main_layout.addWidget(self.coach_list)
        self.main_layout.addWidget(new_group)

    def refresh_list(self):
        self.coach_list.clear()
        query = 'SELECT * FROM coach'
        if text := self.search_field.text():
            [item] = re.findall(USER_PATTERN, text)
            args = tuple(map(lambda s: s.replace('.', '') + '%', item))
            self.cur.execute(query + ' WHERE surname LIKE ? AND name LIKE ? AND lastname LIKE ?', args)
        else:
            self.cur.execute(query)

        tuple(map(lambda cols: self.parse(*cols), self.cur.fetchall()))

    def parse(self, id_: int, surname: str, name: str, lastname: str) -> ListItem:
        return ListItem(self.coach_list, f'{surname} {name} {lastname}', id_)

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.key() == QtCore.Qt.Key_Delete:
            item, = self.coach_list.selectedItems()
            name = item.text()
            resp = QtWidgets.QMessageBox.warning(self,
                                                 'Подтверждение удаления тренера',
                                                 f'Вы действительно хотите удалить тренера {name}?',
                                                 buttons=QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if resp == QtWidgets.QMessageBox.Yes:
                coach_id = item.id
                self.cur.execute('DELETE FROM coach WHERE coach_id = ?', (coach_id,))
                self.db_connection.commit()
                self.refresh_list()

    def add(self):
        surname = self.new_surname.text()
        name = self.new_name.text()
        lastname = self.new_lastname.text()

        self.cur.execute('INSERT INTO coach (surname, name, lastname) VALUES (?, ?, ?)', (surname, name, lastname))
        self.db_connection.commit()
        self.refresh_list()
