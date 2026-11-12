import sys

from PySide6.QtWidgets import QApplication

from src.gesture_assistant.ui.main_window import MainWindow


def main() -> int:
    application = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return application.exec()
