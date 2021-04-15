from PyQt5 import QtWidgets


class List(QtWidgets.QListWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.setStyleSheet('font-size: 32px')
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
