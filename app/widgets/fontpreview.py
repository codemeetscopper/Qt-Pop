from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QScrollArea,
    QHBoxLayout, QFrame, QApplication, QSlider, QSpinBox
)
from PySide6.QtGui import QFont, QPalette
from PySide6.QtCore import Qt


class FontCard(QFrame):
    """Compact modern flat font card using minimal vertical space."""

    def __init__(self, family: str, tag: str, size: int, apply_callback):
        super().__init__()
        self.family = family
        self.tag = tag
        self.apply_callback = apply_callback

        self.setFrameShape(QFrame.NoFrame)
        self.setAutoFillBackground(True)

        pal = self.palette()
        base = pal.color(QPalette.Window)
        pal.setColor(QPalette.Window, base.lighter(104))
        self.setPalette(pal)

        # --- Main layout ---
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(6, 4, 6, 4)
        main_layout.setSpacing(2)

        # --- Top row: Font name, tag, and preview text ---
        top_row = QHBoxLayout()
        top_row.setSpacing(8)

        name_lbl = QLabel(family)
        name_lbl.setFont(QFont(family, 11, QFont.Bold))

        tag_lbl = QLabel(f"({tag})")
        tag_lbl.setFont(QFont("Arial", 9))
        tag_lbl.setEnabled(False)

        self.preview_lbl = QLabel("The quick brown fox jumps over the lazy dog")
        self.preview_lbl.setFont(QFont(family, size))
        self.preview_lbl.setWordWrap(False)
        self.preview_lbl.setSizePolicy(self.sizePolicy())
        self.preview_lbl.setAlignment(Qt.AlignVCenter)

        top_row.addWidget(name_lbl)
        top_row.addWidget(tag_lbl)
        top_row.addSpacing(10)
        top_row.addWidget(self.preview_lbl, 1)

        # --- Bottom row: controls ---
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(6)
        bottom_row.setContentsMargins(0, 0, 0, 0)

        size_lbl = QLabel("Size:")
        size_lbl.setFont(QFont("Arial", 9))

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(8)
        self.slider.setMaximum(48)
        self.slider.setValue(size)
        self.slider.setSingleStep(1)
        self.slider.setFixedWidth(100)

        self.size_spin = QSpinBox()
        self.size_spin.setRange(8, 48)
        self.size_spin.setValue(size)
        self.size_spin.setFixedWidth(50)

        apply_btn = QPushButton("Apply")
        apply_btn.setFont(QFont("Arial", 9, QFont.Medium))
        apply_btn.setAutoDefault(False)
        apply_btn.clicked.connect(self.on_apply_clicked)

        # Synchronize slider and spinbox
        self.slider.valueChanged.connect(self.size_spin.setValue)
        self.size_spin.valueChanged.connect(self.slider.setValue)
        self.slider.valueChanged.connect(self.update_preview_size)

        bottom_row.addWidget(size_lbl)
        bottom_row.addWidget(self.slider)
        bottom_row.addWidget(self.size_spin)
        bottom_row.addStretch()
        bottom_row.addWidget(apply_btn)

        main_layout.addLayout(top_row)
        main_layout.addLayout(bottom_row)

    def update_preview_size(self, value: int):
        """Update preview text font size."""
        self.preview_lbl.setFont(QFont(self.family, value))

    def on_apply_clicked(self):
        size = self.slider.value()
        self.apply_callback(self.tag)


class FontPreviewWidget(QWidget):
    """Scrollable modern compact font viewer for FontManager (no QSS)."""

    def __init__(self, font_manager):
        super().__init__()
        self.font_manager = font_manager
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(6, 6, 6, 6)
        main_layout.setSpacing(4)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        container = QWidget()
        vbox = QVBoxLayout(container)
        vbox.setSpacing(4)
        vbox.setContentsMargins(6, 6, 6, 6)
        vbox.setAlignment(Qt.AlignTop)

        font_map = self.font_manager.get_font_map()
        for tag, info in font_map.items():
            family = info['family']
            size = info['size']
            card = FontCard(family, tag, size, self.apply_font_to_app)
            vbox.addWidget(card)

        scroll.setWidget(container)
        main_layout.addWidget(scroll)

    def apply_font_to_app(self, family: str, size: int):
        """Apply selected font globally."""
        app = QApplication.instance()
        if app:
            app.setFont(QFont(family, size))
        print(f"✅ Applied font: {family}, size {size}")
