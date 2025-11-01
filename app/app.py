import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QScreen

from app.mainwindow.mainwindow import MainWindow
from qtpop import QtPop


def run(qt_pop: QtPop):
    app = QApplication(sys.argv)
    window = MainWindow(qt_pop)

    # Set initial size
    window.resize(1290, 760)

    # --- Center the window on screen ---
    screen = app.primaryScreen()
    screen_geometry = screen.availableGeometry()
    x = (screen_geometry.width() - window.width()) // 2
    y = (screen_geometry.height() - window.height()) // 2
    window.move(x, y)

    window.show()
    sys.exit(app.exec())
