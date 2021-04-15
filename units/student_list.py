import datetime
import sqlite3
import re

from PyQt5 import QtWidgets, QtGui, QtSql, QtCore
from functools import reduce, partial

from window import Window
from static import GENDERS, STUDENT_GRADES, USER_PATTERN
from widgets.combobox import ComboBox
from widgets.table_item import TableItem
from widgets.table import Table
from .student_coach_window import StudentCoachWindow


class StudentList(Window):
    def __init__(self, db_connection: sqlite3.Connection, cursor: sqlite3.Cursor):
        table_headers = ('#', 'ФИО', 'Пол', 'Команда', 'Дата рождения', 'Разряд', 'Тренер')

        super().__init__()

        self.query = QtSql.QSqlQuery()
        self.db_connection = db_connection
        self.cur = cursor

        self.table = Table(headers=table_headers, parent=self)
        self.table.itemDoubleClicked.connect(self.edit_coach)

        self.gender_field = QtWidgets.QComboBox()
        self.gender_field.addItems(('Все',) + GENDERS)
        self.gender_field.currentTextChanged.connect(self.clear_window)

        self.search_field = QtWidgets.QLineEdit()
        self.search_field.setPlaceholderText('ФИО участника')
        self.search_field.returnPressed.connect(self.refresh_list)

        search_layout = QtWidgets.QHBoxLayout()
        search_layout.addWidget(self.search_field)
        search_layout.addWidget(self.gender_field)

        search_groupbox = QtWidgets.QGroupBox('Поиск')
        search_groupbox.setLayout(search_layout)

        self.new_surname = QtWidgets.QLineEdit()
        self.new_surname.setPlaceholderText('Фамилия')

        self.new_name = QtWidgets.QLineEdit()
        self.new_name.setPlaceholderText('Имя')

        self.new_lastname = QtWidgets.QLineEdit()
        self.new_lastname.setPlaceholderText('Отчество')

        self.new_gender = QtWidgets.QComboBox()
        self.new_gender.addItems(GENDERS)

        self.new_born = QtWidgets.QLineEdit()
        self.new_born.setPlaceholderText('Дата рождения')
        self.new_born.setFixedWidth(200)

        organizations = self.get_teams()
        self.new_organization = ComboBox(content=organizations, default_text='Организация')
        self.new_organization.setFixedWidth(200)
        self.new_organization.setStyleSheet('')

        self.new_grade = QtWidgets.QComboBox()
        self.new_grade.addItems(STUDENT_GRADES)

        self.add_button = QtWidgets.QPushButton('Добавить')
        self.add_button.clicked.connect(self.add_new_student)

        add_new_layout = QtWidgets.QHBoxLayout()
        add_widgets = (self.new_surname, self.new_name, self.new_lastname, self.new_gender, self.new_born,
                       self.new_organization, self.new_grade, self.add_button)
        tuple(map(add_new_layout.addWidget, add_widgets))

        add_new_groupbox = QtWidgets.QGroupBox('Добавить нового участника')
        add_new_groupbox.setLayout(add_new_layout)

        self.main_layout.addWidget(search_groupbox)
        self.main_layout.addWidget(self.table)
        self.main_layout.addWidget(add_new_groupbox)

        self.refresh_list()

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        width = self.table.width()
        proportions = (.8, 3, 1, 2, 1, 1, 3)
        for col, prop in enumerate(proportions):
            self.table.setColumnWidth(col, (width * prop) // 12)

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.key() == QtCore.Qt.Key_Delete:
            student_id, name, *_ = map(lambda item: item.text(), self.table.selectedItems())
            resp = QtWidgets.QMessageBox.warning(self, 'Подтверждение удаления студента',
                                                 f'Вы действительно желаете удалить студента {name}?',
                                                 buttons=QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if resp == QtWidgets.QMessageBox.Yes:
                self.cur.execute('DELETE FROM student WHERE student_id = ?', (student_id,))
                self.db_connection.commit()
                self.clear_window()

    def edit_coach(self):
        student_id, name = map(lambda _: _.text(), self.table.selectedItems()[:2])
        window = StudentCoachWindow(self, (student_id, name), self.db_connection, self.cur)
        window.exec_()
        if window.result() == QtWidgets.QDialog.Accepted:
            self.refresh_list()

    def refresh_list(self) -> None:
        self.clear_table()

        query = 'SELECT s.student_id,' \
                's.surname,' \
                's.name,' \
                's.lastname,' \
                'born,' \
                'gender,' \
                't.name as team,' \
                'grade,' \
                "GROUP_CONCAT(c.surname || ' ' || substr(c.name, 0, 2) || '.' || substr(c.lastname, 0, 2)) as coaches " \
                'FROM student s ' \
                'LEFT JOIN coach_student cs on s.student_id = cs.student_id ' \
                'LEFT JOIN coach c on c.coach_id = cs.coach_id ' \
                'INNER JOIN team t on s.team = t.team_id ' \
                'GROUP BY s.student_id'

        conditions = list()
        if text := self.search_field.text():
            [item] = re.findall(USER_PATTERN, text)
            args = tuple(map(lambda s: s.replace('.', '') + '%', item))
            condition = 'surname LIKE ? AND name LIKE ? AND lastname LIKE ?'
            conditions.append((condition, args))

        if self.gender_field.currentText() != 'Все':
            args = (self.gender_field.currentText(),)
            condition = 'gender = ?'
            conditions.append((condition, args))

        if conditions:
            query += ' WHERE ' + ' AND '.join(map(lambda i: i[0], conditions))
            values = reduce(lambda acc, val: (*acc, *val[1]), conditions, tuple())
            self.cur.execute(query, values)
        else:
            self.cur.execute(query)
        for student_id, surname, name, lastname, born, gender, team, grade, coaches in self.cur.fetchall():
            row_idx = self.table.rowCount()
            self.table.insertRow(row_idx)

            def add_row(col_i: int, value: str):
                return self.table.setItem(row_idx, col_i, TableItem(value))

            add_row(0, str(student_id))
            add_row(1, ' '.join((surname, name, lastname)))
            add_row(2, gender)
            add_row(3, team)
            add_row(4, born)
            add_row(6, coaches)

            edit_student_data = partial(self.edit_student_grade, student_id=student_id)
            grade_combobox = ComboBox(content=STUDENT_GRADES, default_text=grade)
            grade_combobox.setEditable(False)
            grade_combobox.setCurrentText(grade)
            grade_combobox.currentTextChanged.connect(edit_student_data)
            self.table.setCellWidget(row_idx, 5, grade_combobox)

        self.table.blockSignals(False)

    def edit_student_grade(self, student_id: int = -1) -> None:
        value = self.sender().currentText()
        self.cur.execute('UPDATE student SET grade = ? WHERE student_id = ?', (value, student_id))
        self.db_connection.commit()

    def get_teams(self) -> tuple:
        self.cur.execute('SELECT name FROM team')
        return reduce(lambda acc, val: (*acc, val[0]), self.cur.fetchall())

    def clear_window(self) -> None:
        self.clear_table()
        self.new_organization.clear()
        self.get_teams()
        self.new_gender.setCurrentText(self.gender_field.currentText())

    def clear_table(self):
        self.table.clearContents()
        self.table.setRowCount(0)

    def add_new_student(self):
        surname, name, lastname = self.new_surname.text(), self.new_name.text(), self.new_lastname.text()
        born = self.new_born.text()
        pattern = '%d.%m.%y' if len(born) == 8 else '%d.%m.%Y'
        gender = self.new_gender.currentText()

        args = (
            surname, name, lastname,
            datetime.datetime.strptime(born, pattern).strftime('%d.%m.%Y'),
            self.new_organization.currentText(),
            gender,
            self.new_grade.currentText()
        )

        query = 'INSERT INTO student (surname, name, lastname, born, team, gender, grade) ' \
                'VALUES (?, ?, ?, ?, (SELECT team_id FROM team WHERE name = ?), ?, ?)'

        self.cur.execute(query, args)
        self.db_connection.commit()
        self.refresh_list()
