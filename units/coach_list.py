import sqlite3
from PyQt5 import QtWidgets, QtGui

from tab import Tab

from widgets.table import Table


class CoachList(Tab):
    def __init__(self, db_connection: sqlite3.Connection, cursor: sqlite3.Cursor):
        super().__init__()

        self.db_connection = db_connection
        self.cur = cursor

        self.coach_list = QtWidgets.QListWidget()
        self.coach_list.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.coach_list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        pass

    def refresh_list(self):
        self.coach_list.clear()
