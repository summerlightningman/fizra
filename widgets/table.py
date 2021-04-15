from PyQt5 import QtWidgets


class Table(QtWidgets.QTableWidget):
    def __init__(self, headers: tuple, parent):
        super().__init__(rows=0, columns=len(headers), parent=parent)

        self.setHorizontalHeaderLabels(headers)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.verticalHeader().hide()
