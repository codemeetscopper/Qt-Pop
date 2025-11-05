from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QPixmap, QGuiApplication
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
)


class IconCardWidget(QWidget):
    copy_clicked = Signal(str)  # emits icon name

    def __init__(self, icon_name: str, size: int, parent=None):
        super().__init__(parent)
        self.icon_name = icon_name
        self.icon_size = size

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)

        # Image
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(size, size)
        self.icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.icon_label)

        # Name row + copy button
        text_row = QHBoxLayout()
        layout.addLayout(text_row)

        self.name_label = QLabel(icon_name)
        self.name_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        text_row.addWidget(self.name_label, stretch=1)

        self.copy_btn = QPushButton("⧉")
        self.copy_btn.setFixedSize(22, 22)
        self.copy_btn.clicked.connect(self.copy_to_clipboard)
        text_row.addWidget(self.copy_btn, alignment=Qt.AlignRight)

    def copy_to_clipboard(self):
        QGuiApplication.clipboard().setText(self.icon_name)
        self.copy_clicked.emit(self.icon_name)

    def update_pixmap(self, pixmap: QPixmap):
        self.icon_label.setPixmap(pixmap.scaled(
            self.icon_size,
            self.icon_size,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        ))
