from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QFileDialog, QColorDialog, QComboBox
)

from app.widgets.colordisplaywidget import ColorDisplayWidget
from qtpop.configuration.models import SettingItem


class SettingItemWidget(QWidget):
    """A single-line, Material-like QWidget for editing a SettingItem."""
    def __init__(self, item: SettingItem, parent=None):
        super().__init__(parent)
        self.colour_display = None
        self.control_layout = QHBoxLayout()
        self.item = item
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 4, 10, 4)
        main_layout.setSpacing(12)

        # --- Left side: Name + Description ---
        label_layout = QVBoxLayout()
        label_layout.setContentsMargins(0, 0, 0, 0)
        label_layout.setSpacing(2)

        label_name = QLabel(self.item.name)
        label_font = QFont()
        label_font.setBold(True)
        label_name.setFont(label_font)
        label_name.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        label_desc = QLabel(self.item.description)
        desc_font = QFont()
        desc_font.setPointSize(desc_font.pointSize() - 1)
        label_desc.setFont(desc_font)
        label_desc.setStyleSheet("color: gray;")  # subtle gray subtext
        label_desc.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        label_layout.addWidget(label_name)
        label_layout.addWidget(label_desc)

        # --- Right side: Value control(s) ---
        self.control_layout.setContentsMargins(0, 0, 0, 0)
        self.control_layout.setSpacing(6)

        self.control = None

        if self.item.type == "text":
            self.control = QLineEdit(str(self.item.value))
            self.control.textChanged.connect(self._on_text_changed)
            self.control_layout.addWidget(self.control)

        elif self.item.type == "filebrowse":
            self.control = QLineEdit(str(self.item.value))
            browse_btn = QPushButton("Browse…")
            browse_btn.clicked.connect(self._browse_file)
            self.control.textChanged.connect(self._on_text_changed)
            self.control_layout.addWidget(self.control)
            self.control_layout.addWidget(browse_btn)

        elif self.item.type == "folderbrowse":
            self.control = QLineEdit(str(self.item.value))
            browse_btn = QPushButton("Browse…")
            browse_btn.clicked.connect(self._browse_folder)
            self.control.textChanged.connect(self._on_text_changed)
            self.control_layout.addWidget(self.control)
            self.control_layout.addWidget(browse_btn)

        elif self.item.type == "colorpicker":
            self.control = QPushButton('Pick')
            self.colour_display = ColorDisplayWidget(QColor(self.item.value), self.item.shortname)
            self.control.clicked.connect(self._pick_color)
            self.control_layout.addWidget(self.colour_display)
            self.control_layout.addWidget(self.control)

        elif self.item.type == "dropdown":
            self.control = QComboBox()
            if isinstance(self.item.values, (list, tuple)):
                self.control.addItems([str(v) for v in self.item.values])
            if self.item.value in self.item.values:
                self.control.setCurrentText(str(self.item.value))
            self.control.currentTextChanged.connect(self._on_dropdown_changed)
            self.control_layout.addWidget(self.control)

        else:
            self.control_layout.addWidget(QLabel(f"Unknown type: {self.item.type}"))

        # --- Combine sections ---
        main_layout.addLayout(label_layout, 2)
        main_layout.addLayout(self.control_layout, 3)
        main_layout.addStretch()

        # Slight elevation hint (material-like spacing)
        self.setMinimumHeight(52)

    # --- Handlers ---
    def _on_text_changed(self, text):
        self.item.value = text

    def _on_dropdown_changed(self, text):
        self.item.value = text

    def _browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "")
        if file_path:
            self.control.setText(file_path)
            self.item.value = file_path

    def _browse_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder", "")
        if folder_path:
            self.control.setText(folder_path)
            self.item.value = folder_path

    def _pick_color(self):
        initial = QColor(self.item.value) if self.item.value else QColor("white")
        color = QColorDialog.getColor(initial, self, "Select Color")
        if color.isValid():
            self.item.value = color.name()
            self._update_color_button(color)

    def _update_color_button(self, color: QColor):
        # Use palette color fill instead of stylesheet
        pal = self.control.palette()
        pal.setColor(self.control.backgroundRole(), color)
        self.control_layout.removeWidget(self.colour_display)
        self.control_layout.removeWidget(self.control)

        self.colour_display.deleteLater()
        self.colour_display = ColorDisplayWidget(color, self.item.shortname)

        self.control_layout.addWidget(self.colour_display)
        self.control_layout.addWidget(self.control)