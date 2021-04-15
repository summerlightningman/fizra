import sqlite3
from PyQt5 import QtWidgets, QtGui

from tab import Tab

from widgets.table import Table


class CoachList(Tab):
    def __init__(self, db_connection: sqlite3.Connection, cursor: sqlite3.Cursor):
        super().__init__()

        self.db_connection = db_connection
        self.cur = cursor

        coach_list = QtWidgets.QListWidget()
        coach_list.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        coach_list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        self.main_layout.addWidget(coach_list)

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        pass
