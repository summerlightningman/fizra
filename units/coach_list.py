import sqlite3
import re

from PyQt5 import QtGui, QtCore, QtWidgets

from tab import Tab
from widgets.list import List
from widgets.list_item import ListItem
from static import USER_PATTERN


class CoachList(Tab):
    def __init__(self, db_connection: sqlite3.Connection, cursor: sqlite3.Cursor):
        super().__init__()

        self.db_connection = db_connection
        self.cur = cursor

        self.search_field = QtWidgets.QLineEdit()
        self.search_field.setPlaceholderText('Поиск по ФИО...')
        self.search_field.returnPressed.connect(self.search)

        search_layout = QtWidgets.QHBoxLayout()
        search_layout.addWidget(self.search_field)

        search_group = QtWidgets.QGroupBox('Поиск тренера')
        search_group.setLayout(search_layout)

        self.coach_list = List(self)
        self.refresh_list()

        self.main_layout.addWidget(search_group)
        self.main_layout.addWidget(self.coach_list)

    def refresh_list(self):
        self.coach_list.clear()
        self.cur.execute('SELECT * FROM coach')
        tuple(ListItem(self.coach_list, f'{surname} {name} {lastname}', id_) for id_, surname, name, lastname in self.cur.fetchall())

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

    def search(self):
        self.coach_list.clear()
        [item] = re.findall(USER_PATTERN, self.search_field.text())
        args = tuple(map(lambda s: '%' + s + '%', item))
        self.cur.execute('SELECT * FROM coach WHERE surname LIKE ? AND name LIKE ? AND lastname LIKE ?', args)
        tuple(ListItem(self.coach_list, f'{surname} {name} {lastname}', id_) for id_, surname, name, lastname in
              self.cur.fetchall())
