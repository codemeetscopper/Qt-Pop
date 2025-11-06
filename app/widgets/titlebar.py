from PySide6.QtCore import Qt, QPoint, QRect
from PySide6.QtGui import QPainter, QColor, QFont, QPen, QIcon, QPolygonF, QCursor
from PySide6.QtWidgets import (
    QWidget, QLabel, QHBoxLayout, QToolButton, QMenu, QApplication, QStyle, QSizeGrip
)


class CustomTitleBar(QWidget):
    """Professional, painter-based custom titlebar for Windows."""
    HEIGHT = 34

    def __init__(self, parent=None, app_icon: QIcon = None, app_name: str = "Application"):
        super().__init__(parent)
        self.parent_window = parent
        self.dragging = False
        self.drag_pos = QPoint()

        self.setFixedHeight(self.HEIGHT)
        self.setMouseTracking(True)
        self.setAutoFillBackground(False)

        # --- App icon (your logo) ---
        self.icon_label = QLabel()
        if app_icon:
            self.icon_label.setPixmap(app_icon.pixmap(20, 20))
        self.icon_label.setFixedSize(26, 26)

        # --- App name ---
        self.title_label = QLabel(app_name)
        font = QFont()
        font.setPointSize(10)
        font.setWeight(QFont.Bold)
        self.title_label.setFont(font)
        self.title_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        # --- Dropdown menu button (with ↓ arrow) ---
        self.menu_button = QToolButton()
        self.menu_button.setAutoRaise(True)
        self.menu_button.setFixedSize(26, 26)
        self.menu_button.setToolTip("Options")
        self.menu = QMenu()
        self.menu.addAction("Settings")
        self.menu.addAction("About")
        self.menu_button.setMenu(self.menu)
        self.menu_button.setPopupMode(QToolButton.InstantPopup)

        # --- Window control buttons ---
        self.min_button = QToolButton()
        self.min_button.setAutoRaise(True)
        self.min_button.setIcon(self.style().standardIcon(QStyle.SP_TitleBarMinButton))
        self.min_button.setFixedSize(26, 26)
        self.min_button.clicked.connect(self._minimize)

        self.max_button = QToolButton()
        self.max_button.setAutoRaise(True)
        self.max_button.setIcon(self.style().standardIcon(QStyle.SP_TitleBarMaxButton))
        self.max_button.setFixedSize(26, 26)
        self.max_button.clicked.connect(self._maximize_restore)

        self.close_button = QToolButton()
        self.close_button.setAutoRaise(True)
        self.close_button.setIcon(self.style().standardIcon(QStyle.SP_TitleBarCloseButton))
        self.close_button.setFixedSize(26, 26)
        self.close_button.clicked.connect(self._close)

        # --- Layout ---
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 0, 4, 0)
        layout.setSpacing(6)
        layout.addWidget(self.icon_label)
        layout.addWidget(self.title_label, 1)
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
        painter.fillRect(rect, QColor(37, 37, 40))

        # Bottom border line
        painter.setPen(QPen(QColor(60, 60, 65)))
        painter.drawLine(0, rect.height() - 1, rect.width(), rect.height() - 1)

        # Draw down arrow for menu button manually (consistent look)
        arrow_rect = self._get_widget_rect(self.menu_button)
        if arrow_rect.isValid():
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(200, 200, 200))
            size = 6
            x = arrow_rect.center().x()
            y = arrow_rect.center().y() + 2
            points = [
                QPoint(x - size // 2, y - size // 4),
                QPoint(x + size // 2, y - size // 4),
                QPoint(x, y + size // 3),
            ]
            painter.drawPolygon(QPolygonF(points))

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
            self.max_button.setIcon(self.style().standardIcon(QStyle.SP_TitleBarMaxButton))
        else:
            self.parent_window.showMaximized()
            self.max_button.setIcon(self.style().standardIcon(QStyle.SP_TitleBarNormalButton))

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
