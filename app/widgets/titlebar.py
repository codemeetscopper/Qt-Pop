from PySide6.QtCore import Qt, QPoint, QRect
from PySide6.QtGui import QPainter, QColor, QFont, QPen, QIcon, QPolygonF, QCursor
from PySide6.QtWidgets import (
    QWidget, QLabel, QHBoxLayout, QToolButton, QMenu, QApplication, QStyle, QSizeGrip
)

from qtpop import QtPop


class CustomTitleBar(QWidget):
    """Professional, painter-based custom titlebar for Windows."""
    HEIGHT = 40

    def __init__(self, qt_pop: QtPop, parent=None, app_icon: QIcon = None, app_name: str = "Application"):
        super().__init__(parent)
        self.parent_window = parent
        self.dragging = False
        self.icon_size = 35
        self.qt_pop = qt_pop
        self.drag_pos = QPoint()

        self.setFixedHeight(self.HEIGHT)
        self.setMouseTracking(True)
        self.setAutoFillBackground(False)

        # --- App icon (your logo) ---
        self.icon_label = QLabel()
        self.icon_label.setPixmap(self.qt_pop.icon.get_pixmap(
            'action join left',
            self.qt_pop.style.get_colour('accent'),
            35
        ))
        self.icon_label.setContentsMargins(0, 0, 0, 0)
        # self.icon_label.setFixedSize(41, 41)

        # --- App name ---
        self.title_label = QLabel(app_name)
        font = QFont()
        font.setPointSize(12)
        font.setWeight(QFont.Bold)
        self.title_label.setFont(font)
        self.title_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.title_label.setStyleSheet(f"color: {self.qt_pop.style.get_colour('accent')};")

        # --- Dropdown menu button (with ↓ arrow) ---
        self.menu_button = QToolButton()
        self.menu_button.setAutoRaise(True)
        self.menu_button.setToolTip("Options")
        self.menu_button.setContentsMargins(0, 0, 0, 0)
        # self.menu = QMenu()
        # self.menu.addAction("Settings")
        # self.menu.addAction("About")
        # self.menu_button.setMenu(self.menu)
        self.menu_button.setPopupMode(QToolButton.InstantPopup)
        self.menu_button.setIcon(self.qt_pop.icon.get_pixmap(
            'action info outline',
            self.qt_pop.style.get_colour('fg2'),
            self.icon_size
        ))

        # --- Window control buttons ---
        self.min_button = QToolButton()
        self.min_button.setAutoRaise(True)
        self.min_button.setContentsMargins(5, 0, 0, 0)
        self.min_button.setIcon(self.qt_pop.icon.get_pixmap(
            'action minimize',
            self.qt_pop.style.get_colour('fg1'),
            self.icon_size
        ))
        self.min_button.clicked.connect(self._minimize)

        self.max_button = QToolButton()
        self.max_button.setAutoRaise(True)
        self.max_button.setContentsMargins(5, 0, 0, 0)
        self.max_button.setIcon(self.qt_pop.icon.get_pixmap(
            'navigation fullscreen',
            self.qt_pop.style.get_colour('fg1'),
            self.icon_size
        ))
        self.max_button.clicked.connect(self._maximize_restore)

        self.close_button = QToolButton()
        self.close_button.setAutoRaise(True)
        self.close_button.setContentsMargins(5, 0, 0, 0)
        self.close_button.setIcon(self.qt_pop.icon.get_pixmap(
            'navigation close',
            self.qt_pop.style.get_colour('fg1'),
            self.icon_size
        ))
        self.close_button.clicked.connect(self._close)

        # --- Layout ---
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(5)
        layout.addWidget(self.icon_label, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.title_label, 1, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.menu_button)
        layout.addWidget(self.min_button)
        layout.addWidget(self.max_button)
        layout.addWidget(self.close_button)
        self.setLayout(layout)

        # --- Resize grips ---
        self._create_grips()

    # -------------------
    # Resize grips
    # -------------------
    def _create_grips(self):
        self.grips = [QSizeGrip(self) for _ in range(4)]
        for g in self.grips:
            g.setVisible(False)

    def resizeEvent(self, event):
        if not self.parent_window:
            return
        grip_size = 12
        rect = self.parent_window.rect()
        self.grips[0].setGeometry(QRect(rect.left(), rect.top(), grip_size, grip_size))
        self.grips[1].setGeometry(QRect(rect.right() - grip_size, rect.top(), grip_size, grip_size))
        self.grips[2].setGeometry(QRect(rect.left(), rect.bottom() - grip_size, grip_size, grip_size))
        self.grips[3].setGeometry(QRect(rect.right() - grip_size, rect.bottom() - grip_size, grip_size, grip_size))

    # -------------------
    # Painting
    # -------------------
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect()

        # Background
        # painter.fillRect(rect, self.qt_pop.style.get_colour('bg', to_str=False))

        # Bottom border line
        painter.setPen(QPen(self.qt_pop.style.get_colour('accent_l3', to_str=False)))
        painter.drawLine(0, rect.height() - 1, rect.width(), rect.height() - 1)

        # Draw down arrow for menu button manually (consistent look)
        # arrow_rect = self._get_widget_rect(self.menu_button)
        # if arrow_rect.isValid():
        #     painter.setPen(Qt.NoPen)
        #     painter.setBrush(QColor(200, 200, 200))
        #     size = 6
        #     x = arrow_rect.center().x()
        #     y = arrow_rect.center().y() + 2
        #     points = [
        #         QPoint(x - size // 2, y - size // 4),
        #         QPoint(x + size // 2, y - size // 4),
        #         QPoint(x, y + size // 3),
        #     ]
        #     painter.drawPolygon(QPolygonF(points))

    def _get_widget_rect(self, widget: QWidget) -> QRect:
        """Get absolute geometry of a child widget in parent coordinates."""
        if not widget:
            return QRect()
        pos = widget.pos()
        return QRect(pos, widget.size())

    # -------------------
    # Window control
    # -------------------
    def _minimize(self):
        if self.parent_window:
            self.parent_window.showMinimized()

    def _maximize_restore(self):
        if not self.parent_window:
            return
        if self.parent_window.isMaximized():
            self.parent_window.showNormal()
            self.max_button.setIcon(self.qt_pop.icon.get_pixmap(
            'navigation fullscreen',
            self.qt_pop.style.get_colour('fg2'),
            self.icon_size
        ))
        else:
            self.parent_window.showMaximized()
            self.max_button.setIcon(self.qt_pop.icon.get_pixmap(
            'navigation fullscreen exit',
            self.qt_pop.style.get_colour('fg2'),
            self.icon_size
        ))

    def _close(self):
        if self.parent_window:
            self.parent_window.close()

    # -------------------
    # Mouse events (drag + double click)
    # -------------------
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_pos = event.globalPos() - self.parent_window.frameGeometry().topLeft()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.dragging and event.buttons() == Qt.LeftButton:
            self.parent_window.move(event.globalPos() - self.drag_pos)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.dragging = False
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._maximize_restore()


# -------------------
# Example usage
# -------------------
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget

    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
            self.resize(900, 550)

            icon = QIcon(r"resources/images/meterialicons/action_chrome_reader_mode_materialiconsround_24px.svg")  # replace with your logo path
            self.titlebar = CustomTitleBar(self, icon, "OdxUtility Dashboard")

            central = QWidget()
            layout = QVBoxLayout(central)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            layout.addWidget(self.titlebar)
            layout.addStretch(1)
            self.setCentralWidget(central)

    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
