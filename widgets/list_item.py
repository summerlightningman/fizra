from PyQt5 import QtWidgets


class ListItem(QtWidgets.QListWidgetItem):
    def __init__(self, parent, text, id_):
        super().__init__(text, parent)

        self.id = id_
