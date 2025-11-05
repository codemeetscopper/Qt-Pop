import sys
import os
from PySide6.QtCore import Qt, QSize, Slot
from PySide6.QtGui import QPixmap, QColor, QImage
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QComboBox, QListWidget, QListWidgetItem,
    QSpinBox, QColorDialog, QMessageBox
)

from qtpop import IconManager


# -----------------------------
# Icon Grid widget (pure view)
# -----------------------------
class IconGrid(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setViewMode(QListWidget.IconMode)
        self.setResizeMode(QListWidget.Adjust)
        self.setSpacing(12)
        self.setMovement(QListWidget.Static)
        self.setUniformItemSizes(False)
        self.setSelectionMode(self.SelectionMode.SingleSelection)


    def update_icon(self, name: str, pixmap: QPixmap):
        """Update existing icon card when async pixmap arrives."""
        for i in range(self.count()):
            item = self.item(i)
            if item.text() == name:
                item.setIcon(pixmap)
                return

import sys
import os
from PySide6.QtCore import Qt, QSize, Slot
from PySide6.QtGui import QPixmap, QColor, QImage
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QComboBox, QListWidget, QListWidgetItem,
    QSpinBox, QColorDialog, QMessageBox
)

from qtpop import IconManager   # ✅ updated import
from test2 import IconCardWidget


class IconBrowserWidget(QWidget):
    def __init__(self, parent=None, images_path="resources/images"):
        super().__init__(parent)

        if os.path.isdir(images_path):
            IconManager.set_images_path(images_path)

        self.current_color = "#FFFFFF"
        self.current_size = 28
        self.icons = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(12)

        # ------------------- Controls -------------------
        control = QHBoxLayout()
        layout.addLayout(control)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search…")
        self.search_box.textChanged.connect(self.apply_filter)
        control.addWidget(self.search_box, stretch=2)

        self.color_selector = QComboBox()
        self.color_selector.addItems(["accent", "support", "neutral", "fg", "bg"])
        self.color_selector.currentTextChanged.connect(self.on_color_tag)
        control.addWidget(self.color_selector)

        self.pick_btn = QPushButton("🎨")
        self.pick_btn.setFixedWidth(36)
        self.pick_btn.clicked.connect(self.pick_color)
        control.addWidget(self.pick_btn)

        self.size_spin = QSpinBox()
        self.size_spin.setRange(12, 128)
        self.size_spin.setValue(self.current_size)
        self.size_spin.valueChanged.connect(self.on_size)
        control.addWidget(self.size_spin)

        self.refresh_btn = QPushButton("⟳")
        self.refresh_btn.setFixedWidth(36)
        self.refresh_btn.clicked.connect(self.reload)
        control.addWidget(self.refresh_btn)

        # ------------------- Grid -------------------
        self.grid = QListWidget()
        self.grid.setViewMode(QListWidget.IconMode)
        self.grid.setResizeMode(QListWidget.Adjust)
        self.grid.setSpacing(12)
        self.grid.setMovement(QListWidget.Static)
        self.grid.setUniformItemSizes(False)
        layout.addWidget(self.grid)

        IconManager._notifier.icon_loaded.connect(self.on_icon_loaded)

        self.reload()

    # ------------------- Controls action -------------------

    def on_color_tag(self):
        self.current_color = self._resolve_color(
            self.color_selector.currentText())
        self.reload()

    def pick_color(self):
        col = QColorDialog.getColor(QColor(self.current_color), self)
        if col.isValid():
            self.current_color = col.name()
            self.reload()

    def on_size(self, v):
        self.current_size = v
        self.reload()

    # Plug into your theme later
    def _resolve_color(self, tag: str) -> str:
        return {
            "accent": "#00BCD4",
            "support": "#9C27B0",
            "neutral": "#9E9E9E",
            "fg": "#FFFFFF",
            "bg": "#000000",
        }.get(tag, "#FFFFFF")

    # ------------------- Icon loader pipeline -------------------

    def reload(self):
        self.icons = IconManager.list_icons()
        self.apply_filter()

    def apply_filter(self):
        query = self.search_box.text().strip()
        filtered = IconManager.search_icons(query, self.icons) if query else sorted(self.icons)
        self.grid.clear()

        for name in filtered:
            item = QListWidgetItem(self.grid)
            card = IconCardWidget(name, self.current_size)
            item.setSizeHint(QSize(self.current_size + 40, self.current_size + 50))
            self.grid.setItemWidget(item, card)

            IconManager.get_pixmap(name, self.current_color, self.current_size,
                                   async_load=True)

    # ------------------- Async Update Handler -------------------

    @Slot(str, object)
    def on_icon_loaded(self, name: str, obj):
        if isinstance(obj, QImage):
            pixmap = QPixmap.fromImage(obj)
        elif isinstance(obj, QPixmap):
            pixmap = obj
        else:
            return

        for i in range(self.grid.count()):
            item = self.grid.item(i)
            card = self.grid.itemWidget(item)
            if card and card.icon_name == name:
                card.update_pixmap(pixmap)


# ------------------------------
# Standalone preview
# ------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = IconBrowserWidget(images_path="resources/images/meterialicons/")
    w.setWindowTitle("🔍 Icon Browser")
    w.resize(900, 550)
    w.show()
    sys.exit(app.exec())
