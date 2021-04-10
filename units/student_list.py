import re
import datetime

from PyQt5 import QtWidgets, QtGui, QtSql
from functools import reduce, partial

from tab import Tab
from static import DATE_PATTERN, GENDERS, GRADES
from widgets.combobox import ComboBox
from widgets.student_combobox import StudentComboBox
from widgets.delete_button import DeleteButton


class StudentList(Tab):
    def __init__(self, db_connection, cursor):
        self.TABLE_HEADERS = ('#', 'ФИО', 'Пол', 'Команда', 'Дата рождения', 'Время забега', 'Разряд', 'Удалить')

        super().__init__()

        self.query = QtSql.QSqlQuery()
        self.db_connection = db_connection
        self.cur = cursor

        self.table = QtWidgets.QTableWidget(0, len(self.TABLE_HEADERS), self)
        self.table.setHorizontalHeaderLabels(self.TABLE_HEADERS)
        self.table.cellChanged.connect(self.edit_text_student_data)

        self.gender_dropdown = QtWidgets.QComboBox()
        self.gender_dropdown.addItems(('Все',) + GENDERS)
        self.gender_dropdown.currentTextChanged.connect(self.refresh_data)

        self.search_input = QtWidgets.QLineEdit()
        self.search_input.setPlaceholderText('ФИО участника')
        self.search_input.returnPressed.connect(self.get_data)

        search_layout = QtWidgets.QHBoxLayout()
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.gender_dropdown)

        search_groupbox = QtWidgets.QGroupBox('Поиск')
        search_groupbox.setLayout(search_layout)

        self.new_name = QtWidgets.QLineEdit()
        self.new_name.setPlaceholderText('ФИО участника')

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
        self.new_grade.addItems(GRADES)

        self.add_button = QtWidgets.QPushButton('Добавить')
        self.add_button.clicked.connect(self.add_new_student)

        add_new_layout = QtWidgets.QHBoxLayout()
        add_new_layout.addWidget(self.new_name)
        add_new_layout.addWidget(self.new_gender)
        add_new_layout.addWidget(self.new_born)
        add_new_layout.addWidget(self.new_organization)
        add_new_layout.addWidget(self.new_grade)
        add_new_layout.addWidget(self.add_button)

        add_new_groupbox = QtWidgets.QGroupBox('Добавить нового участника')
        add_new_groupbox.setLayout(add_new_layout)

        self.main_layout.addWidget(search_groupbox)
        self.main_layout.addWidget(self.table)
        self.main_layout.addWidget(add_new_groupbox)

        self.get_data()

    def edit_text_student_data(self):
        student_id = int(self.table.item(self.table.currentRow(), 0).text())
        return self.edit_student_data(student_id=student_id)

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        headers_count = len(self.TABLE_HEADERS)
        col_width = self.table.width() // headers_count
        for i in range(headers_count - 1):
            self.table.setColumnWidth(i, col_width)

    def get_data(self):
        self.clear_table()
        self.table.blockSignals(True)
        second_name = self.search_input.text() + '%'
        gender = '' if self.gender_dropdown.currentText() == 'Все' else self.gender_dropdown.currentText()

        query = 'SELECT ' \
                'studentId, secondName, firstName, lastName, dateOfBirth, gender, t.name as team, ' \
                'runtime, grade, s.team as team_id ' \
                'FROM students s INNER JOIN teams t on s.team = t.team_id'
        if gender and second_name != '%':
            query += ' WHERE gender = ? AND secondName LIKE ?'
            args = (gender, second_name)
        elif gender:
            query += ' WHERE gender = ?'
            args = (gender,)
        elif second_name != '%':
            query += ' WHERE secondName LIKE ?'
            args = (second_name,)
        else:
            args = tuple()

        for student_id, surname, name, lastname, born, gender, team, runtime, grade, team_id \
                in self.db_connection.execute(query, args):
            row_idx = self.table.rowCount()
            self.table.insertRow(row_idx)

            def add_row(col_i: int, value: str):
                return self.table.setItem(row_idx, col_i, QtWidgets.QTableWidgetItem(value))

            add_row(0, str(student_id))
            add_row(1, ' '.join((surname, name, lastname)))
            add_row(4, born)
            add_row(5, runtime)

            edit_student_data = partial(self.edit_student_data, student_id=student_id)
            gender_combobox = StudentComboBox(
                content=GENDERS, default_text=gender, field='gender'
            )
            gender_combobox.setEditable(False)
            gender_combobox.setCurrentText(gender)
            gender_combobox.currentTextChanged.connect(edit_student_data)
            self.table.setCellWidget(row_idx, 2, gender_combobox)

            teams = self.get_teams()
            team_combobox = StudentComboBox(
                content=teams, default_text=team, field='team'
            )
            team_combobox.setEditText(team)
            team_combobox.currentTextChanged.connect(edit_student_data)
            self.table.setCellWidget(row_idx, 3, team_combobox)

            grade_combobox = StudentComboBox(
                content=GRADES, default_text=grade, field='grade'
            )
            grade_combobox.setEditable(False)
            grade_combobox.setCurrentText(grade)
            grade_combobox.currentTextChanged.connect(edit_student_data)
            self.table.setCellWidget(row_idx, 6, grade_combobox)

            delete_button = DeleteButton(text='Удалить', id_=student_id)
            delete_button.clicked.connect(self.delete_student)
            self.table.setCellWidget(row_idx, 7, delete_button)
        self.table.blockSignals(False)

    def edit_student_data(self, student_id: int = -1):
        sender = self.sender()
        if hasattr(sender, 'currentText'):
            key = sender.field
            if key == 'team':
                (value,) = self.db_connection.execute('SELECT team_id FROM teams WHERE name = ?',
                                                      (sender.currentText(),)).fetchone()
            else:
                value = sender.currentText()
        else:
            col = self.table.currentColumn()
            key = self.table.horizontalHeaderItem(col).text()
            if key in ('ФИО', '#'):
                return
            elif key == 'Дата рождения':
                key = 'dateOfBirth'
            elif key == 'Время забега':
                key = 'runtime'
            value = self.table.currentItem().text()

        self.cur.execute("UPDATE students SET {} = ? WHERE studentId = ?".format(key), (value, student_id))
        self.db_connection.commit()

    def delete_student(self):
        student_id = self.sender().id
        response = QtWidgets.QMessageBox.question(
            self, 'Подтверждение удаления участника',
            f'Вы действительно хотите удалить участника #{student_id}?',
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if response == 16384:
            self.cur.execute('DELETE FROM students WHERE studentId = ?', (student_id,))
            self.db_connection.commit()
            self.refresh_data()

    def get_teams(self) -> tuple:
        self.cur.execute('SELECT name FROM teams')
        return reduce(lambda acc, val: (*acc, val[0]), self.cur.fetchall())

    def refresh_data(self):
        self.clear_table()
        self.get_data()
        self.new_organization.clear()
        self.get_teams()
        self.new_gender.setCurrentText(self.gender_dropdown.currentText())
        self.search_input.clear()

    def clear_table(self):
        self.table.clearContents()
        self.table.setRowCount(0)

    def add_new_student(self):
        name_args = self.new_name.text().strip().split(' ')
        if len(name_args) == 2:
            name_args.append('')

        [(day, month, year)] = re.findall(DATE_PATTERN, self.new_born.text())

        if len(year) == 2:
            curr_year = datetime.datetime.now().year
            year = ('19' + year) if int('20' + year) > curr_year else (20 + year)
        gender = self.new_gender.currentText()[0]

        args = (
            *name_args,
            '{}.{}.{}'.format(
                day if len(day) == 2 else ('0' + day),
                month if len(day) == 2 else ('0' + day),
                year
            ),
            self.new_organization.currentText(),
            gender,
            self.new_grade.currentText()
        )
        query = 'INSERT INTO students (secondName, firstName, lastName, dateOfBirth, team, gender, grade) ' \
                'VALUES (?, ?, ?, ?, ?, ?, ?)'

        self.cur.execute(query, args)
        self.db_connection.commit()
        self.refresh_data()
