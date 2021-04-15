import sqlite3

from PyQt5 import QtWidgets, QtGui, QtCore
from tab import Tab

from widgets.table import Table
from widgets.table_item import TableItem
from widgets.combobox import ComboBox

from functools import reduce


class TeamList(Tab):
    def __init__(self, db_connection: sqlite3.Connection, cursor: sqlite3.Cursor):
        super().__init__()

        table_headers = ('#', 'Наименование', 'Первенство')

        self.db_connection = db_connection
        self.cur = cursor

        self.table = Table(headers=table_headers, parent=self)

        self.search_input = QtWidgets.QLineEdit()
        self.search_input.setPlaceholderText('Наименование команды')
        self.search_input.returnPressed.connect(self.get_data)

        search_input_layout = QtWidgets.QHBoxLayout()
        search_input_layout.addWidget(self.search_input)

        search_input_group = QtWidgets.QGroupBox('Поиск команды по наименованию')
        search_input_group.setLayout(search_input_layout)

        self.new_name = QtWidgets.QLineEdit()
        self.new_name.setPlaceholderText('Имя новой команды')

        points = self.get_points()
        self.new_points = ComboBox(content=points, default_text='Командное первенство')
        self.new_points.setFixedWidth(400)
        self.new_points.setStyleSheet('')

        add_button = QtWidgets.QPushButton('Добавить')
        add_button.clicked.connect(self.add_team)

        add_new_layout = QtWidgets.QHBoxLayout()
        add_new_layout.addWidget(self.new_name)
        add_new_layout.addWidget(self.new_points)
        add_new_layout.addWidget(add_button)

        add_new_group = QtWidgets.QGroupBox('Добавить новую команду')
        add_new_group.setLayout(add_new_layout)

        self.main_layout.addWidget(search_input_group)
        self.main_layout.addWidget(self.table)
        self.main_layout.addWidget(add_new_group)

        self.get_data()

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        width = self.table.width()
        self.table.setColumnWidth(0, (width * 1 // 12) - 20)
        self.table.setColumnWidth(1, (width * 8 // 12) - 20)
        self.table.setColumnWidth(2, (width * 3 // 12) - 20)

    def get_data(self):
        self.clear_table()
        team_name = self.search_input.text()
        query = 'SELECT * FROM team'

        if team_name:
            query += ' WHERE name LIKE ?'
            args = ('%' + team_name + '%',)
        else:
            args = tuple()

        self.table.blockSignals(True)
        for team_id, name, points in self.db_connection.execute(query, args):
            row_idx = self.table.rowCount()
            self.table.insertRow(row_idx)

            def add_row(col_i, value):
                return self.table.setItem(row_idx, col_i, TableItem(value))

            add_row(0, str(team_id))
            add_row(1, name)
            add_row(2, points)
        self.table.blockSignals(False)

    def clear_table(self):
        self.table.clearContents()
        self.table.setRowCount(0)

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        team_id, name, _ = tuple(map(lambda item: item.text(), self.table.selectedItems()))
        if event.key() == QtCore.Qt.Key_Delete:
            result = QtWidgets.QMessageBox.question(
                self, 'Подтверждение удаления команды',
                f'Вы действительно хотите удалить команду "{name}"?',
                buttons=QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )
            if result == QtWidgets.QMessageBox.Yes:
                self.cur.execute('DELETE FROM team WHERE team_id = ?', (team_id,))
                self.db_connection.commit()
                self.get_data()

    def get_points(self) -> tuple:
        self.cur.execute('SELECT DISTINCT points FROM team')
        return reduce(lambda acc, val: (*acc, *val), self.cur.fetchall())

    def add_team(self):
        name = self.new_name.text()
        points = self.new_points.currentText()
        if name and points:
            self.cur.execute('INSERT INTO team (name, points) VALUES (?, ?)', (name, points))
            self.db_connection.commit()
            self.get_data()
