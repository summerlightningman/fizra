import sqlite3
import os

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWebEngineWidgets import QWebEngineView
from tab import Tab

from static import PROTOCOLS, DOCUMENTS_PATH


class ProtocolList(Tab):
    def __init__(self, db_connection: sqlite3.Connection, cursor: sqlite3.Cursor):
        super().__init__()

        self.db_connection = db_connection
        self.cur = cursor

        self.type_combobox = QtWidgets.QComboBox()
        self.type_combobox.addItems(PROTOCOLS)

        type_layout = QtWidgets.QHBoxLayout()
        type_layout.addWidget(self.type_combobox)

        type_group = QtWidgets.QGroupBox('Вид протокола')
        type_group.setLayout(type_layout)

        generate_button = QtWidgets.QPushButton('Сгенерировать')
        generate_button.clicked.connect(self.generate_protocol)

        self.view = QWebEngineView()
        self.view.loadFinished.connect(self.to_pdf)

        self.main_layout.addWidget(type_group)
        self.main_layout.addWidget(self.view)
        self.main_layout.addWidget(generate_button)

    def to_pdf(self, _):
        page = DOCUMENTS_PATH + '/docs.pdf'
        layout = QtGui.QPageLayout(
            QtGui.QPageSize(QtGui.QPageSize.A4),
            QtGui.QPageLayout.Landscape,
            QtCore.QMarginsF(0, 0, 0, 0)
        )
        self.view.page().printToPdf(page, layout)

    def generate_protocol(self):
        url = QtCore.QUrl('file:///' + DOCUMENTS_PATH.replace('\\', '/') + '/index.html')
        self.view.setUrl(url)
