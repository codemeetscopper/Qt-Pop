from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QHBoxLayout, QFrame, QApplication, QSpinBox, QSizePolicy
)
from PySide6.QtGui import QFont, QPalette, QColor, QPainter, QPainterPath
from PySide6.QtCore import Qt, QRectF


class FontCard(QFrame):
    """Compact horizontal font card with rounded design and proper spinbox behavior."""

    def __init__(self, family: str, tag: str, size: int, apply_callback):
        super().__init__()
        self.family = family
        self.tag = tag
        self.apply_callback = apply_callback
        self.radius = 10
        self.current_size = size  # track current size

        # --- Appearance ---
        self.setAutoFillBackground(True)
        pal = self.palette()
        pal.setColor(QPalette.Window, QColor(250, 250, 252))
        self.setPalette(pal)

        # --- Main Layout ---
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(12, 6, 12, 6)
        main_layout.setSpacing(12)
        main_layout.setAlignment(Qt.AlignVCenter)

        # --- Tag ---
        tag_lbl = QLabel(f"{tag}")
        tag_lbl.setStyleSheet("QLabel { font-size: 16px; font-weight: bold; }")
        tag_lbl.setFixedWidth(90)

        # --- Font Name ---
        name_lbl = QLabel(family)
        name_lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        name_lbl.setFixedWidth(120)

        # --- Preview ---
        self.preview_lbl = QLabel("The quick brown fox jumps over the lazy dog")
        self.preview_lbl.setFont(QFont(family, size))
        self.preview_lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.preview_lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.preview_lbl.setMinimumWidth(300)

        # --- Size Control ---
        size_container = QWidget()
        size_layout = QHBoxLayout(size_container)
        size_layout.setContentsMargins(0, 0, 0, 0)
        size_layout.setSpacing(4)
        size_layout.setAlignment(Qt.AlignVCenter)

        size_lbl = QLabel("Size:")

        self.size_spin = QSpinBox()
        self.size_spin.setRange(8, 72)
        self.size_spin.setValue(size)
        self.size_spin.setFixedWidth(80)
        self.size_spin.setAlignment(Qt.AlignRight)
        self.size_spin.valueChanged.connect(self.update_preview_size)

        size_layout.addWidget(size_lbl)
        size_layout.addWidget(self.size_spin)
        size_container.setFixedWidth(150)

        # --- Apply Button ---
        apply_btn = QPushButton("Try font")
        apply_btn.setCursor(Qt.PointingHandCursor)
        apply_btn.setAutoDefault(False)
        apply_btn.setFixedWidth(70)
        apply_btn.clicked.connect(self.on_apply_clicked)

        # --- Assemble Layout ---
        main_layout.addWidget(tag_lbl)
        main_layout.addWidget(name_lbl)
        main_layout.addWidget(self.preview_lbl, 1)
        main_layout.addWidget(size_container)
        main_layout.addWidget(apply_btn)

    # --- Custom paint for rounded corners ---
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = QRectF(self.rect())
        path = QPainterPath()
        path.addRoundedRect(rect.adjusted(0.5, 0.5, -0.5, -0.5), self.radius, self.radius)
        painter.fillPath(path, self.palette().color(QPalette.Window))
        painter.setPen(QColor(225, 225, 230))
        painter.drawPath(path)
        super().paintEvent(event)

    # --- Update preview dynamically ---
    def update_preview_size(self, value: int):
        """Update preview text font size and store it."""
        self.current_size = value
        self.preview_lbl.setFont(QFont(self.family, value))

    # --- Apply button handler ---
    def on_apply_clicked(self):
        """Trigger external apply callback with latest tag and size."""
        self.apply_callback(self.tag, self.current_size)
