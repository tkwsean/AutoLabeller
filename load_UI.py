import os
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog, QDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QShortcut
from load_image import LoadImage
from magnifyingglass import MagnifyingGlass
from renameDialogue import RenameDialog  # Import the RenameDialog class

class LoadUI:
    def __init__(self, parent):
        self.parent = parent

    def initUI(self):
        self.parent.setWindowTitle('Image Inspector')

        self.label = QLabel('No Image Loaded', self.parent)
        self.label.setAlignment(Qt.AlignCenter)

        self.remaining_label = QLabel('Remaining: 0', self.parent)
        self.remaining_label.setAlignment(Qt.AlignCenter)
        
        self.completed_label = QLabel('Completed: 0', self.parent)
        self.completed_label.setAlignment(Qt.AlignCenter)

        self.button_frame = QHBoxLayout()  # Use QHBoxLayout to stack buttons horizontally

        self.next_button = QPushButton('Next Image Pair', self.parent)
        self.next_button.clicked.connect(self.parent.load_next_image_pair)
        self.button_frame.addWidget(self.next_button)

        self.correct_button = QPushButton('Correct', self.parent)
        self.correct_button.clicked.connect(self.handle_correct)
        # Vertical layout for Single and Double buttons
        single_double_frame = QVBoxLayout()
        single_double_frame.addWidget(self.correct_button)
        
        self.single_button = QPushButton('Single', self.parent)  # Correctly define single_button here
        self.single_button.clicked.connect(self.handle_correct_single)
        single_double_frame.addWidget(self.single_button)

        self.double_button = QPushButton('Double', self.parent)
        self.double_button.clicked.connect(self.handle_correct_double)
        single_double_frame.addWidget(self.double_button)

        self.button_frame.addLayout(single_double_frame)  # Add vertical layout to horizontal layout

        self.incorrect_blurred_button = QPushButton('imageblur', self.parent)
        self.incorrect_blurred_button.clicked.connect(self.handle_blur)
        self.button_frame.addWidget(self.incorrect_blurred_button)
        
        self.ignore_button = QPushButton('ignore', self.parent)
        self.ignore_button.clicked.connect(lambda: self.parent.rename_and_move_image('ignore'))
        self.button_frame.addWidget(self.ignore_button)

        self.incorrect_missing_object_button = QPushButton('doubleline', self.parent)
        self.incorrect_missing_object_button.clicked.connect(lambda: self.parent.rename_and_move_image('doubleline'))
        self.button_frame.addWidget(self.incorrect_missing_object_button)
        
        self.incorrect_keypoint_error_button = QPushButton('keypointerror', self.parent)
        self.incorrect_keypoint_error_button.clicked.connect(self.handle_keypoint_error)  # Update the connection
        self.button_frame.addWidget(self.incorrect_keypoint_error_button)
        
        self.incorrect_others_button = QPushButton('others', self.parent)
        self.incorrect_others_button.clicked.connect(lambda: self.parent.rename_and_move_image('others'))
        self.button_frame.addWidget(self.incorrect_others_button)

        self.image_label = QLabel(self.parent)
        self.image_label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.remaining_label)
        layout.addWidget(self.completed_label)
        layout.addLayout(self.button_frame)  # Add button_frame (QVBoxLayout) to the main layout
        layout.addWidget(self.image_label)

        self.parent.setLayout(layout)

        self.image_files = QFileDialog.getExistingDirectory(self.parent, "Select Folder with Images")
        self.loader = LoadImage(self.image_files, self.image_label, self.label, self.remaining_label, self.completed_label)
        self.magnifier = MagnifyingGlass(self.loader)
        self.loader.magnifier = self.magnifier

        self.parent.loader = self.loader  # Ensure the loader attribute is set on the parent
        self.assign_methods_to_parent()

        self.update_counts()
        self.initShortcuts()
        self.parent.setMouseTracking(True)
        self.image_label.setMouseTracking(True)
        self.image_label.mouseMoveEvent = self.magnifier.mouseMoveEvent

    def assign_methods_to_parent(self):
        self.parent.update_counts = self.loader.update_counts
        self.parent.load_next_image_pair = self.loader.load_next_image_pair
        self.parent.move_image = self.loader.move_image
        self.parent.rename_and_move_image = self.rename_and_move_image  # Add this line

    def update_counts(self):
        self.loader.update_counts()

    def initShortcuts(self):
        QShortcut(QKeySequence('1'), self.parent).activated.connect(self.handle_correct)
        QShortcut(QKeySequence('2'), self.parent).activated.connect(self.handle_correct_single)
        QShortcut(QKeySequence('3'), self.parent).activated.connect(self.handle_correct_double)
        QShortcut(QKeySequence('6'), self.parent).activated.connect(self.handle_blur)
        QShortcut(QKeySequence('7'), self.parent).activated.connect(self.handle_keypoint_error)  # Update the connection
        QShortcut(QKeySequence('8'), self.parent).activated.connect(lambda: self.parent.rename_and_move_image('ignore'))
        QShortcut(QKeySequence('9'), self.parent).activated.connect(lambda: self.parent.rename_and_move_image('doubleline'))
        QShortcut(QKeySequence('0'), self.parent).activated.connect(lambda: self.parent.rename_and_move_image('others'))
    def rename_and_move_image(self, category):
        dialog = RenameDialog(self.parent)
        if dialog.exec_() == QDialog.Accepted:
            new_name = dialog.get_new_name()
            if new_name:
                self.parent.loader.move_image(category, new_name)

    def handle_keypoint_error(self):
        # Directly move to the keypointerror folder without prompt
        self.parent.loader.move_image('keypointerror', None)
    
    def handle_correct(self):
        self.parent.loader.move_image('correct', None)
        
    def handle_correct_single(self):
        self.parent.loader.move_image('correct/single', None)
    
    def handle_correct_double(self):
        self.parent.loader.move_image('correct/double', None)
        
    def handle_blur(self):
        self.parent.loader.move_image('imageblur', None)


