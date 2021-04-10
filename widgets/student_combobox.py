from .combobox import ComboBox


class StudentComboBox(ComboBox):
    def __init__(self, content, default_text, field):
        super().__init__(content, default_text)
        self.field = field
