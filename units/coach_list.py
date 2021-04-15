import sqlite3
from PyQt5 import QtWidgets, QtGui

from tab import Tab

from widgets.list_item import ListItem


class CoachList(Tab):
    def __init__(self, db_connection: sqlite3.Connection, cursor: sqlite3.Cursor):
        super().__init__()

        self.db_connection = db_connection
        self.cur = cursor

        self.coach_list = QtWidgets.QListWidget()
        self.coach_list.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.coach_list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.refresh_list()

        self.main_layout.addWidget(self.coach_list)

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        pass

    def refresh_list(self):
        self.coach_list.clear()
        self.cur.execute('SELECT * FROM coach')
        tuple(ListItem(self.coach_list, f'{surname} {name} {lastname}', id_) for id_, surname, name, lastname in self.cur.fetchall())
