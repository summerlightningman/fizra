import sqlite3
from PyQt5 import QtWidgets

from tab import Tab

from widgets.table import Table

class CoachList(Tab):
    def __init__(self, db_connection, cursor):
        super().__init__()

        self.db_connection = db_connection
        self.cur = cur

        self.table = Table
