import sqlite3

from PyQt5 import QtWidgets, QtGui
from widgets.list_item import ListItem


class StudentCoachWindow(QtWidgets.QDialog):
    def __init__(self, parent, student: tuple, db_connection: sqlite3.Connection, cursor: sqlite3.Cursor):
        super().__init__(parent)
        student_id, name = student

        self.resize(800, 400)
        self.setWindowTitle('Указать тренеров')

        self.db_connection = db_connection
        self.cur = cursor
        self.to_add = []
        self.to_remove = []

        label = QtWidgets.QLabel(f'Указать тренеров для студента <b>{name}</b>:')

        ok_button = QtWidgets.QPushButton('ОК')
        ok_button.clicked.connect(self.accept)

        cancel_button = QtWidgets.QPushButton('Отмена')
        cancel_button.clicked.connect(self.reject)

        bottom_layout = QtWidgets.QHBoxLayout()
        bottom_layout.addWidget(ok_button)
        bottom_layout.addWidget(cancel_button)

        add_button = QtWidgets.QPushButton('>>')
        add_button.setMaximumWidth(30)
        add_button.clicked.connect(self.add)

        remove_button = QtWidgets.QPushButton('<<')
        remove_button.setMaximumWidth(30)
        remove_button.clicked.connect(self.remove)

        control_layout = QtWidgets.QVBoxLayout()
        control_layout.addWidget(add_button)
        control_layout.addWidget(remove_button)

        self.all_coach_list = QtWidgets.QListWidget(self)

        self.student_coach_list = QtWidgets.QListWidget(self)

        middle_layout = QtWidgets.QHBoxLayout()
        middle_layout.addWidget(self.all_coach_list)
        middle_layout.addLayout(control_layout)
        middle_layout.addWidget(self.student_coach_list)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(label)
        main_layout.addLayout(middle_layout)
        main_layout.addLayout(bottom_layout)

        self.setLayout(main_layout)

        self.student_id = student_id
        self.get_data()

    def get_data(self):
        query = 'SELECT c.coach_id, c.surname, c.name, c.lastname FROM coach_student cs ' \
                'INNER JOIN coach c on cs.coach_id = c.coach_id '
        self.cur.execute(query + 'WHERE student_id != ?', (self.student_id,))
        tuple(ListItem(self.all_coach_list, f'{surname} {name} {lastname}', coach_id)
              for coach_id, surname, name, lastname in self.cur.fetchall())

        self.cur.execute(query + 'WHERE student_id = ?', (self.student_id,))
        tuple(ListItem(self.student_coach_list, f'{surname} {name} {lastname}', coach_id)
              for coach_id, surname, name, lastname in self.cur.fetchall())

    def add(self):
        if items := self.all_coach_list.selectedItems():
            item = self.all_coach_list.takeItem(self.all_coach_list.row(items[0]))
            self.student_coach_list.addItem(item)
            self.define_operations('add', item.id)

    def remove(self):
        if items := self.student_coach_list.selectedItems():
            item = self.student_coach_list.takeItem(self.student_coach_list.row(items[0]))
            self.all_coach_list.addItem(item)
            self.define_operations('remove', item.id)

    def define_operations(self, operation, id_):
        if operation == 'add':
            if id_ in self.to_remove:
                self.to_remove.remove(id_)
            else:
                self.to_add.append(id_)
        elif operation == 'remove':
            if id_ in self.to_add:
                self.to_add.remove(id_)
            else:
                self.to_remove.append(id_)

    def accept(self) -> None:
        if self.to_add:
            ids = tuple(map(lambda num: (self.student_id, num), self.to_add))
            self.cur.executemany(f'INSERT INTO coach_student (student_id, coach_id) VALUES (?, ?)', ids)
        if self.to_remove:
            ids = tuple(map(lambda num: (self.student_id, num), self.to_remove))
            self.cur.executemany(f'DELETE FROM coach_student WHERE student_id = ? AND coach_id = ?', ids)
        self.db_connection.commit()
        self.done(1)