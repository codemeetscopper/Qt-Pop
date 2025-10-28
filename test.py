from dataclasses import dataclass, field
from typing import Any
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QFileDialog, QColorDialog, QComboBox, QApplication
)
from PySide6.QtGui import QColor, QFont
from PySide6.QtCore import Qt
import sys


@dataclass
class SettingItem:
    name: str
    value: Any
    values: Any
    description: str
    type: str  # 'text', 'filebrowse', 'folderbrowse', 'colorpicker', 'dropdown'
    accessibility: str
    group: str
    icon: str = field(default='')


class SettingItemWidget(QWidget):
    """A single-line, Material-like QWidget for editing a SettingItem."""

    def __init__(self, item: SettingItem, parent=None):
        super().__init__(parent)
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
        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(0, 0, 0, 0)
        control_layout.setSpacing(6)

        self.control = None

        if self.item.type == "text":
            self.control = QLineEdit(str(self.item.value))
            self.control.textChanged.connect(self._on_text_changed)
            control_layout.addWidget(self.control)

        elif self.item.type == "filebrowse":
            self.control = QLineEdit(str(self.item.value))
            browse_btn = QPushButton("Browse…")
            browse_btn.clicked.connect(self._browse_file)
            self.control.textChanged.connect(self._on_text_changed)
            control_layout.addWidget(self.control)
            control_layout.addWidget(browse_btn)

        elif self.item.type == "folderbrowse":
            self.control = QLineEdit(str(self.item.value))
            browse_btn = QPushButton("Browse…")
            browse_btn.clicked.connect(self._browse_folder)
            self.control.textChanged.connect(self._on_text_changed)
            control_layout.addWidget(self.control)
            control_layout.addWidget(browse_btn)

        elif self.item.type == "colorpicker":
            self.control = QPushButton()
            self._update_color_button(QColor(self.item.value))
            self.control.clicked.connect(self._pick_color)
            control_layout.addWidget(self.control)

        elif self.item.type == "dropdown":
            self.control = QComboBox()
            if isinstance(self.item.values, (list, tuple)):
                self.control.addItems([str(v) for v in self.item.values])
            if self.item.value in self.item.values:
                self.control.setCurrentText(str(self.item.value))
            self.control.currentTextChanged.connect(self._on_dropdown_changed)
            control_layout.addWidget(self.control)

        else:
            control_layout.addWidget(QLabel(f"Unknown type: {self.item.type}"))

        # --- Combine sections ---
        main_layout.addLayout(label_layout, 2)
        main_layout.addLayout(control_layout, 3)
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
        self.control.setAutoFillBackground(True)
        self.control.setPalette(pal)
        self.control.setText(color.name())


# --- Demo Window ---
if __name__ == "__main__":
    app = QApplication(sys.argv)

    example_items = [
        SettingItem("Username", "john_doe", None, "Your account username", "text", "", "General"),
        SettingItem("Config File", "", None, "Path to configuration file", "filebrowse", "", "Paths"),
        SettingItem("Workspace", "", None, "Select your workspace directory", "folderbrowse", "", "Paths"),
        SettingItem("Accent Color", "#3498db", None, "Theme accent color", "colorpicker", "", "Appearance"),
        SettingItem("Theme", "Light", ["Light", "Dark", "System"], "Choose your app theme", "dropdown", "", "Appearance"),
    ]

    window = QWidget()
    layout = QVBoxLayout(window)
    layout.setContentsMargins(12, 12, 12, 12)
    layout.setSpacing(10)

    for item in example_items:
        layout.addWidget(SettingItemWidget(item))

    window.setWindowTitle("Settings Example")
    window.resize(600, 300)
    window.show()

    sys.exit(app.exec())
