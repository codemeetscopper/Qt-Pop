from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QSizePolicy
)

class IconCardWidget(QWidget):
    copy_requested = Signal(str)

    def __init__(self, name: str, pix: QPixmap = None, size: int = 32, parent=None):
        super().__init__(parent)
        self.name = name
        self.size = size

        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("background: none;")  # ✅ no stylesheet later for design

        # ------- Top Bar (Copy Button aligned Right) -------
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(0, 0, 0, 0)

        top_bar.addStretch()
        self.copy_btn = QPushButton("⧉")
        self.copy_btn.setFixedSize(20, 20)
        self.copy_btn.clicked.connect(self.emit_copy)
        top_bar.addWidget(self.copy_btn)

        # ------- Icon Centered -------
        self.icon_lbl = QLabel()
        self.icon_lbl.setAlignment(Qt.AlignCenter)
        self.icon_lbl.setFixedSize(size + 4, size + 4)  # breathing space

        # ------- Icon Name Centered -------
        self.text_lbl = QLabel(name)
        self.text_lbl.setAlignment(Qt.AlignCenter)
        self.text_lbl.setWordWrap(False)

        # ------- Main Vertical Layout -------
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        layout.addLayout(top_bar)
        layout.addWidget(self.icon_lbl, alignment=Qt.AlignCenter)
        layout.addWidget(self.text_lbl, alignment=Qt.AlignCenter)
        layout.addStretch()

        self._update_pixmap(pix)

        # Sensible size policy (grid-friendly)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

    # Public method to update image when async returns
    def set_pixmap(self, pix: QPixmap):
        self._update_pixmap(pix)

    def _update_pixmap(self, pix):
        if pix:
            scaled = pix.scaled(
                self.size, self.size,
                Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.icon_lbl.setPixmap(scaled)

    def emit_copy(self):
        self.copy_requested.emit(self.name)
