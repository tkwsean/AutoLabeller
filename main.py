# main.py
import os
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QShortcut
from PyQt5.QtGui import QKeySequence
from load_UI import LoadUI

# Get the path to the current conda environment
conda_env_path = sys.prefix
qt_plugin_path = os.path.join(conda_env_path, "lib", "python3.12", "site-packages", "PyQt5", "Qt", "plugins")

# Set the QT_QPA_PLATFORM_PLUGIN_PATH environment variable
os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = qt_plugin_path

class ImageInspector(QWidget):
    def __init__(self):
        super().__init__()
        self.load_ui = LoadUI(self)
        self.load_ui.initUI()
        self.load_ui.assign_methods_to_parent()

    def load_next_image_pair(self):
        self.loader.load_next_image_pair()

    def move_image(self, category, new_name):
        self.loader.move_image(category, new_name)

    def update_counts(self):
        self.loader.update_counts()

if __name__ == "__main__":
    app = QApplication([])
    inspector = ImageInspector()
    inspector.show()
    app.exec_()
