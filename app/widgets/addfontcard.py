from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QFileDialog, QSpinBox, QSizePolicy
)
from PySide6.QtGui import QFont, QPalette, QColor, QPainter, QPainterPath
from PySide6.QtCore import Qt, QRectF


class AddFontCard(QFrame):
    """Minimal, modern card to add new fonts, styled like FontCard."""

    def __init__(self, add_font_callback):
        """
        :param add_font_callback: function(file_path, tag, size)
        """
        super().__init__()
        self.add_font_callback = add_font_callback
        self.font_path = ""
        self.radius = 10

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

        # --- Tag Input ---
        tag_lbl = QLabel("Tag")
        tag_lbl.setStyleSheet("QLabel { font-weight: bold; font-size: 16px; }")
        tag_lbl.setFixedWidth(40)

        self.tag_edit = QLineEdit()
        self.tag_edit.setPlaceholderText("e.g., h1")
        self.tag_edit.setFixedWidth(90)

        # --- Font File Picker ---
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Select .ttf / .otf file")
        self.path_edit.setReadOnly(True)
        self.path_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.path_edit.setMinimumWidth(260)

        browse_btn = QPushButton("Browse")
        browse_btn.setFixedWidth(70)
        browse_btn.clicked.connect(self.browse_font)

        # --- Size Control ---
        size_lbl = QLabel("Size")
        self.size_spin = QSpinBox()
        self.size_spin.setRange(8, 72)
        self.size_spin.setValue(12)
        self.size_spin.setFixedWidth(70)
        self.size_spin.setAlignment(Qt.AlignRight)

        # --- Add Button ---
        add_btn = QPushButton("Add font")
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setFixedWidth(70)
        add_btn.clicked.connect(self.add_font)

        # --- Assemble Layout ---
        main_layout.addWidget(tag_lbl)
        main_layout.addWidget(self.tag_edit)
        main_layout.addWidget(self.path_edit, 1)
        main_layout.addWidget(browse_btn)
        main_layout.addWidget(size_lbl)
        main_layout.addWidget(self.size_spin)
        main_layout.addWidget(add_btn)

    # --- Rounded paint ---
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

    # --- Browse font file ---
    def browse_font(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Font File", "", "Font Files (*.ttf *.otf)"
        )
        if file_path:
            self.font_path = file_path
            self.path_edit.setText(file_path.split("/")[-1])

    # --- Add font callback ---
    def add_font(self):
        tag = self.tag_edit.text().strip()
        size = self.size_spin.value()

        if not self.font_path or not tag:
            print("Font file or tag missing.")
            return

        self.add_font_callback(self.font_path, tag, size)
        print(f"Added font: {self.font_path}, tag={tag}, size={size}")

        # Reset fields
        self.path_edit.clear()
        self.tag_edit.clear()
        self.size_spin.setValue(12)
        self.font_path = ""
