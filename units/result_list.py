import sqlite3
import re

from static import PROTOCOLS
from window import Window
from widgets.table import Table
from widgets.table_item import TableItem

from PyQt5 import QtWidgets, QtGui


class ResultList(Window):
    def __init__(self, db_connection: sqlite3.Connection, cursor: sqlite3.Cursor):
        super().__init__()

        self.db_connection = db_connection
        self.cur = cursor

        search_field = QtWidgets.QLineEdit()
        search_field.setPlaceholderText('ФИО студента, дата рождения')

        search_combobox = QtWidgets.QComboBox()
        search_combobox.addItems(('Все',) + PROTOCOLS)

        search_layout = QtWidgets.QHBoxLayout()
        search_layout.addWidget(search_field)
        search_layout.addWidget(search_combobox)

        search_group = QtWidgets.QGroupBox('Поиск студента')
        search_group.setLayout(search_layout)

        header_list = 'ФИО студента', 'Дата рождения', 'Команда', 'Вид', 'Этап', 'Результат'
        self.table = Table(parent=self, headers=header_list)
        self.refresh_data()

        self.main_layout.addWidget(search_group)
        self.main_layout.addWidget(self.table)

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        width = self.table.width()
        proportions = (3, 2, 3, 2, 2, 2)
        sum_ = sum(proportions)
        for col, prop in enumerate(proportions):
            self.table.setColumnWidth(col, (width * prop // sum_) - 5)

    def refresh_data(self):
        self.table.setRowCount(0)
        query = "SELECT (s.surname || ' ' || s.name || ' ' || s.lastname) as student, " \
                "s.born, t.name as team, type, stage, time FROM result r" \
                "INNER JOIN student s on rINNER.student_id = s.student_id " \
                "INNER JOIN team t on t.team_id = s.team"

        self.cur.execute(query)

        col_count = self.table.columnCount()
        for values in self.cur.fetchall():
            row_index = self.table.rowCount()
            self.table.insertRow(row_index)

            def set_cell(col: int, value: str):
                self.table.setItem(row_index, col, TableItem(value))

            tuple(map(set_cell, range(col_count), values))
