"""Compact widget used in the demo icon gallery."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QSizePolicy, QVBoxLayout, QWidget


class IconCardWidget(QWidget):
    """Small tile showing an icon preview with a copy action."""

    copy_requested = Signal(str)

    def __init__(self, name: str, pixmap: QPixmap | None = None, size: int = 32, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("IconCard")
        self.setAttribute(Qt.WA_StyledBackground, True)

        self._name = name
        self._size = size

        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(0, 0, 0, 0)
        top_bar.addStretch(1)

        self._copy_button = QPushButton("Copy")
        self._copy_button.setObjectName("IconCopyButton")
        self._copy_button.setFixedHeight(22)
        self._copy_button.clicked.connect(self._emit_copy)
        top_bar.addWidget(self._copy_button)

        self._icon_label = QLabel()
        self._icon_label.setFixedSize(size + 12, size + 12)
        self._icon_label.setAlignment(Qt.AlignCenter)

        self._name_label = QLabel(name)
        self._name_label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)
        layout.addLayout(top_bar)
        layout.addWidget(self._icon_label, alignment=Qt.AlignCenter)
        layout.addWidget(self._name_label)
        layout.addStretch(1)

        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        if pixmap is not None:
            self.set_pixmap(pixmap)

    def set_pixmap(self, pixmap: QPixmap) -> None:
        scaled = pixmap.scaled(self._size, self._size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self._icon_label.setPixmap(scaled)

    def _emit_copy(self) -> None:
        self.copy_requested.emit(self._name)
