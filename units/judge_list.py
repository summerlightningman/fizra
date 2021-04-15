from tab import Tab
from PyQt5 import QtWidgets, QtGui, QtCore

# from widgets.delete_button import DeleteButton
from widgets.tree_item import TreeItem

from functools import reduce


class JudgeList(Tab):
    def __init__(self, db_connection, cursor):
        super().__init__()

        self.db_connection = db_connection
        self.cur = cursor

        header_labels = ('Категория', 'ФИО', 'Удалить')
        self.table = QtWidgets.QTreeWidget()
        self.table.setHeaderLabels(header_labels)
        self.table.setColumnCount(2)
        self.table.setColumnWidth(0, 400)
        self.table.setStyleSheet('font-size: 32px')

        self.new_name = QtWidgets.QLineEdit()
        self.new_name.setPlaceholderText('ФИО судьи')

        types = self.get_judge_types()
        self.new_type = QtWidgets.QComboBox()
        self.new_type.addItems(types)

        self.add_button = QtWidgets.QPushButton('Добавить')
        self.add_button.clicked.connect(self.add_judge)

        add_layout = QtWidgets.QHBoxLayout()
        add_layout.addWidget(self.new_name)
        add_layout.addWidget(self.new_type)
        add_layout.addWidget(self.add_button)

        new_group = QtWidgets.QGroupBox('Добавить нового судью')
        new_group.setLayout(add_layout)

        self.main_layout.addWidget(self.table)
        self.main_layout.addWidget(new_group)
        self.refresh()

    def refresh(self) -> None:
        self.table.clear()
        judge_types = self.get_judge_types()
        for type_ in judge_types:
            item = QtWidgets.QTreeWidgetItem(self.table)
            item.setText(0, type_)
            self.get_data_for_type(type_, item)

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.key() == QtCore.Qt.Key_Delete:
            item, = self.table.selectedItems()
            if hasattr(item, 'id'):
                name = item.text(1)
                resp = QtWidgets.QMessageBox.warning(self, 'Подтверждение удаления судьи',
                                                     'Вы действительно желаете удалить судью {}?'.format(name),
                                                     QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                if resp == QtWidgets.QMessageBox.Yes:
                    self.cur.execute('DELETE FROM judges WHERE judge_id = ?', (item.id,))
                    self.db_connection.commit()
                    self.refresh()

    def get_data_for_type(self, name: str, parent: QtWidgets.QTreeWidgetItem):
        self.cur.execute('SELECT judge_id, surname, name, lastname FROM judges WHERE type IN '
                         '(SELECT type_id FROM judge_types WHERE name = ?)', (name,))

        for id_, surname, name, lastname in self.cur.fetchall():
            # item = QtWidgets.QTreeWidgetItem(parent)
            item = TreeItem(id_, parent)
            item.setText(1, f'{surname} {name} {lastname if lastname else ""}')
            # delete_button = DeleteButton(text='Удалить', id_=id_)
            # delete_button.clicked.connect(self.delete_judge)
            # self.table.setItemWidget(item, 2, delete_button)

    # def delete_judge(self):
    #     judge_id = self.sender().id
    #     response = QtWidgets.QMessageBox.question(
    #         self, 'Подтверждение удаления участника',
    #         f'Вы действительно хотите удалить судью #{judge_id}?',
    #         QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
    #     )
    #     if response == QtWidgets.QMessageBox.Yes:
    #         judge_id = self.sender().id
    #         self.cur.execute('DELETE FROM judges WHERE judge_id = ?', (judge_id,))
    #         self.db_connection.commit()
    #     self.get_data()

    def get_judge_types(self) -> tuple:
        self.cur.execute('SELECT name FROM judge_types')
        return reduce(lambda acc, val: (*acc, *val), self.cur.fetchall())

    def add_judge(self) -> None:
        name = self.new_name.text().split(' ')
        type_ = self.new_type.currentText()

        if len(name) == 2:
            query = 'INSERT INTO judges (surname, name, type) VALUES (?, ?, ' \
                    '(SELECT type_id FROM judge_types WHERE name = ?))'
        elif len(name) == 3:
            query = 'INSERT INTO judges (surname, name, lastname, type) VALUES (?, ?, ?, (SELECT type_id FROM ' \
                    'judge_types WHERE name = ?)) '
        else:
            return

        self.cur.execute(query, (*name, type_))
        self.db_connection.commit()
        self.refresh()
