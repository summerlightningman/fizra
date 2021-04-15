from PyQt5 import QtWidgets


class TreeItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, id_: int = -1, *args):
        super().__init__(*args)

        self.id = id_
