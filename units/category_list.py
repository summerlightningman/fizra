import sqlite3
from window import Window

from PyQt5 import QtWidgets, QtGui, QtCore

from widgets.list_item import ListItem
from widgets.list import List


class CategoryList(Window):
    def __init__(self, db_connection: sqlite3.Connection, cursor: sqlite3.Cursor):
        super().__init__()

        self.db_connection = db_connection
        self.cur = cursor

        self.category_list = List(self)
        self.refresh_list()

        self.new_name = QtWidgets.QLineEdit()
        self.new_name.setPlaceholderText('Имя новой категории')
        self.new_name.returnPressed.connect(self.add_category)

        add_button = QtWidgets.QPushButton('Добавить')
        add_button.clicked.connect(self.add_category)

        add_layout = QtWidgets.QHBoxLayout()
        add_layout.addWidget(self.new_name)
        add_layout.addWidget(add_button)

        add_group = QtWidgets.QGroupBox('Добавить новую категорию')
        add_group.setLayout(add_layout)

        self.main_layout.addWidget(self.category_list)
        self.main_layout.addWidget(add_group)

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.key() == QtCore.Qt.Key_Delete:
            item, = self.category_list.selectedItems()
            name = item.text()
            resp = QtWidgets.QMessageBox.warning(self, 'Подтверждение удаления категории',
                                                 f'Вы действительно желаете удалить категорию {name}? Все судьи и '
                                                 'участники, относящиеся к этой категории также будут удалены.',
                                                 buttons=QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if resp == QtWidgets.QMessageBox.Yes:
                type_id = item.id
                self.cur.execute('DELETE FROM judge_type WHERE type_id = ?', (type_id,))
                self.db_connection.commit()
                self.refresh_list()

    def add_category(self):
        name = self.new_name.text()
        self.cur.execute('INSERT INTO judge_type (name) VALUES (?)', (name,))
        self.db_connection.commit()
        self.refresh_list()
        self.new_name.clear()

    def refresh_list(self) -> None:
        self.category_list.clear()
        self.cur.execute('SELECT * FROM judge_type')
        tuple(ListItem(self.category_list, category, category_id) for (category_id, category,) in self.cur.fetchall())
