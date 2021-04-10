from PyQt5 import QtWidgets, QtCore


class ComboBox(QtWidgets.QComboBox):
    def __init__(self, content, default_text):
        super().__init__(parent=None)

        self.addItems(content)

        self.setEditable(True)

        completer = QtWidgets.QCompleter(content, parent=self)
        completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.setCompleter(completer)

        self.setStyleSheet('background:white;border:none')
        self.setEditText(default_text)
