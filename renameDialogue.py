# rename_dialog.py
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout

class RenameDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.new_name = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Rename File')

        layout = QVBoxLayout()

        self.label = QLabel('Enter new name for the file:', self)
        layout.addWidget(self.label)

        self.line_edit = QLineEdit(self)
        layout.addWidget(self.line_edit)

        self.button_box = QHBoxLayout()

        self.ok_button = QPushButton('OK', self)
        self.ok_button.clicked.connect(self.accept)
        self.button_box.addWidget(self.ok_button)

        self.cancel_button = QPushButton('Cancel', self)
        self.cancel_button.clicked.connect(self.reject)
        self.button_box.addWidget(self.cancel_button)

        layout.addLayout(self.button_box)

        self.setLayout(layout)

    def accept(self):
        self.new_name = self.line_edit.text()
        super().accept()

    def reject(self):
        self.new_name = None
        super().reject()

    def get_new_name(self):
        return self.new_name
