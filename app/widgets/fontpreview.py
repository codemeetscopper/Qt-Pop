from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QScrollArea,
    QHBoxLayout, QFrame, QApplication, QSlider, QSpinBox
)
from PySide6.QtGui import QFont, QPalette
from PySide6.QtCore import Qt


class FontCard(QFrame):
    """A compact card showing one font with live size control."""

    def __init__(self, family: str, tag: str, size: int, apply_callback):
        super().__init__()
        self.family = family
        self.tag = tag
        self.apply_callback = apply_callback

        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setAutoFillBackground(True)

        # Slight tone change for card background
        pal = self.palette()
        base_col = pal.color(QPalette.Window)
        pal.setColor(QPalette.Window, base_col.lighter(102))
        self.setPalette(pal)

        self.preview_label = QLabel("The quick brown fox jumps over the lazy dog")
        self.preview_label.setFont(QFont(family, size))
        self.preview_label.setSizePolicy(self.sizePolicy())

        # --- Header row (font name + tag) ---
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)

        name_lbl = QLabel(family)
        name_lbl.setFont(QFont(family, 12, QFont.Bold))

        tag_lbl = QLabel(f"[{tag}]")
        tag_lbl.setFont(QFont("Arial", 10, QFont.Normal))
        tag_lbl.setEnabled(False)

        header_layout.addWidget(name_lbl)
        header_layout.addWidget(tag_lbl)
        header_layout.addStretch()

        # --- Font size control row ---
        control_layout = QHBoxLayout()
        control_layout.setSpacing(6)

        size_lbl = QLabel("Size:")
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(8)
        self.slider.setMaximum(48)
        self.slider.setValue(size)
        self.slider.setSingleStep(1)
        self.slider.setFixedWidth(120)

        self.size_spin = QSpinBox()
        self.size_spin.setRange(8, 48)
        self.size_spin.setValue(size)

        apply_btn = QPushButton("Apply")
        apply_btn.setAutoDefault(False)
        apply_btn.clicked.connect(self.on_apply_clicked)

        # Synchronize slider + spinbox
        self.slider.valueChanged.connect(self.size_spin.setValue)
        self.size_spin.valueChanged.connect(self.slider.setValue)
        self.slider.valueChanged.connect(self.update_preview_size)

        control_layout.addWidget(size_lbl)
        control_layout.addWidget(self.slider)
        control_layout.addWidget(self.size_spin)
        control_layout.addWidget(apply_btn)

        # --- Combine layouts ---
        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        layout.setContentsMargins(8, 8, 8, 8)

        layout.addLayout(header_layout)
        layout.addWidget(self.preview_label)
        layout.addLayout(control_layout)

    def update_preview_size(self, value: int):
        """Update preview text font size."""
        self.preview_label.setFont(QFont(self.family, value))

    def on_apply_clicked(self):
        size = self.slider.value()
        self.apply_callback(self.tag)


class FontPreviewWidget(QWidget):
    """Scrollable font viewer for FontManager — minimal, no QSS."""

    def __init__(self, font_manager):
        super().__init__()
        self.font_manager = font_manager
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        container = QWidget()
        vbox = QVBoxLayout(container)
        vbox.setSpacing(6)
        vbox.setContentsMargins(8, 8, 8, 8)
        vbox.setAlignment(Qt.AlignTop)

        # --- Create cards from font map ---
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
