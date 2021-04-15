import sqlite3

from PyQt5 import QtWidgets, QtGui
from tab import Tab
from widgets.delete_button import DeleteButton
from widgets.combobox import ComboBox

from functools import reduce


class TeamList(Tab):
    def __init__(self, db_connection: sqlite3.Connection, cursor: sqlite3.Cursor):
        super().__init__()

        self.TABLE_HEADERS = ('#', 'Наименование', 'Первенство', 'Удалить')

        self.db_connection = db_connection
        self.cur = cursor

        self.table = QtWidgets.QTableWidget(0, len(self.TABLE_HEADERS), self)
        self.table.setHorizontalHeaderLabels(self.TABLE_HEADERS)
        self.table.cellChanged.connect(self.edit_team_data)

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
        self.table.setColumnWidth(0, width * 1 // 12)
        self.table.setColumnWidth(1, width * 8 // 12)
        self.table.setColumnWidth(2, width * 2 // 12)

    def get_data(self):
        self.clear_table()
        team_name = self.search_input.text()
        query = 'SELECT * FROM teams'

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
                return self.table.setItem(row_idx, col_i, QtWidgets.QTableWidgetItem(value))

            add_row(0, str(team_id))
            add_row(1, name)
            add_row(2, points)

            delete_button = DeleteButton('Удалить', team_id)
            delete_button.clicked.connect(self.delete_team)
            self.table.setCellWidget(row_idx, 3, delete_button)
        self.table.blockSignals(False)

    def clear_table(self):
        self.table.clearContents()
        self.table.setRowCount(0)

    def edit_team_data(self, row, col):
        col_labels = ('team_id', 'name', 'points')
        team_id = self.table.item(row, 0).text()
        value = self.table.item(row, col).text()

        col_name = col_labels[col]
        query = 'UPDATE teams SET {} = ? WHERE team_id = ?'.format(col_name)
        args = (value, team_id)
        self.cur.execute(query, args)
        self.db_connection.commit()

    def delete_team(self):
        team_id = self.sender().id
        result = QtWidgets.QMessageBox.question(
            self, 'Подтверждение удаления команды',
            f'Вы действительно хотите удалить команду #{team_id}?'
        )
        if result == 16384:
            self.cur.execute('DELETE FROM teams WHERE team_id = ?', (team_id,))
            self.db_connection.commit()
            self.get_data()

    def get_points(self) -> tuple:
        self.cur.execute('SELECT DISTINCT points FROM teams')
        return reduce(lambda acc, val: (*acc, *val), self.cur.fetchall())

    def add_team(self):
        name = self.new_name.text()
        points = self.new_points.currentText()
        if name and points:
            self.cur.execute('INSERT INTO teams (name, points) VALUES (?, ?)', (name, points))
            self.db_connection.commit()
            self.get_data()
