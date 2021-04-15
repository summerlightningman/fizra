from PyQt5 import QtWidgets

from tab import Tab

class CoachList(Tab):
    def __init__(self, db_connection, cur):
        super().__init__()

        self.table = QtWidgets.QTableWidget()
