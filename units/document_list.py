import os

from PyQt5 import QtWidgets

from static import DOCUMENTS_PATH
from tab import Tab


class DocumentList(Tab):
    def __init__(self):
        super().__init__()

        if not os.path.exists(DOCUMENTS_PATH):
            os.mkdir(DOCUMENTS_PATH)

        files = self.list_files()

        document_list = QtWidgets.QListWidget()
        document_list.setStyleSheet('font-size: 32px;')
        self.fill_content_in_list(document_list, files)
        document_list.itemDoubleClicked.connect(self.open_file)

        search_field = QtWidgets.QLineEdit()
        search_field.setStyleSheet('font-size: 24px;')
        search_field.setPlaceholderText('Поиск файла...')
        search_field.returnPressed.connect(lambda: self.search_files(files, document_list))

        self.main_layout.addWidget(search_field)
        self.main_layout.addWidget(document_list)

    @staticmethod
    def fill_content_in_list(list_widget: QtWidgets.QListWidget, content) -> tuple:
        list_widget.clear()
        return tuple(map(lambda file: QtWidgets.QListWidgetItem(file, list_widget), content))

    @staticmethod
    def open_file(item: QtWidgets.QListWidgetItem):
        filename = item.text()
        filepath = os.path.join(DOCUMENTS_PATH, filename)
        return os.system(filepath)

    @staticmethod
    def list_files() -> list:
        return os.listdir(DOCUMENTS_PATH)

    def search_files(self, collection: list, list_widget: QtWidgets.QListWidget):
        query = self.sender().text()
        result = tuple(filter(lambda file: query in file, collection))
        return self.fill_content_in_list(list_widget, result)
