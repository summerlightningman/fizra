from PyQt5 import QtWidgets
from tab import Tab


class ProtocolList(Tab):
    def __init__(self, db_connection, cursor):
        super().__init__()

        self.db_connection = db_connection
        self.cur = cursor

        self.type_combobox = QtWidgets.QComboBox()

        type_layout = QtWidgets.QHBoxLayout()
        type_layout.addWidget(self.type_combobox)

        type_group = QtWidgets.QGroupBox('Вид протокола')
        type_group.setLayout(type_layout)

        self.main_layout.addWidget(type_group)
