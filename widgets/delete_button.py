from PyQt5 import QtWidgets


class DeleteButton(QtWidgets.QPushButton):
    def __init__(self, text, id_):
        super().__init__(text)
        self.id = id_
