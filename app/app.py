import sys

from PySide6.QtWidgets import QApplication

from app.mainwindow.mainwindow import MainWindow
from qtpop import QtPop


def run(qt_pop: QtPop):
    app = QApplication(sys.argv)
    window = MainWindow(qt_pop)
    window.show()
    sys.exit(app.exec())