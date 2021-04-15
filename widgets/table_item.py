from PyQt5 import QtWidgets, QtCore


class TableItem(QtWidgets.QTableWidgetItem):
    def __init__(self, *args):
        super().__init__(*args)
        self.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
