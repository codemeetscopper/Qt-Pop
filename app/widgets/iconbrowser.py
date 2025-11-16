import os
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QPainter, QColor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QScrollArea, QGridLayout, QFrame, QSizePolicy, QSpinBox
)

from qtpop import IconManager, QtPop


from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
from PySide6.QtGui import QPixmap, QPainter
from PySide6.QtCore import Qt


class IconCardWidget(QWidget):
    """Displays a single icon with its name below, auto-wraps long names and scales card size proportionally."""

    def __init__(self, icon_name: str, pixmap: QPixmap, qt_pop, parent=None, icon_size=48):
        super().__init__(parent)
        self.icon_name = icon_name
        self.pixmap = pixmap
        self.qt_pop = qt_pop
        self.icon_size = icon_size

        # Base layout
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(9)

        # Icon display
        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setFixedSize(icon_size + 16, icon_size + 16)
        self.icon_label.setPixmap(self.pixmap.scaled(icon_size, icon_size, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        layout.addWidget(self.icon_label, alignment=Qt.AlignCenter)

        # Name label
        self.name_label = QLabel(self._split_text(icon_name))
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setWordWrap(True)
        layout.addWidget(self.name_label)

        # Make card size proportional to icon
        max_width = int(icon_size * 3.2)
        max_height = int(icon_size * 3.8)
        self.setFixedSize(max_width, max_height)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.setLayout(layout)

    def _split_text(self, text: str, max_len=10):
        """Split long text into two lines if needed."""
        if len(text) <= max_len:
            return text
        words = text.split("_")
        if len(words) > 1:
            half = len(words) // 2
            return " ".join(words[:half]) + "\n" + " ".join(words[half:])
        else:
            return text[:max_len] + "\n" + text[max_len:]

    def update_icon(self, pixmap: QPixmap, size: int):
        """Update the displayed icon pixmap and adjust its size."""
        self.icon_label.setPixmap(pixmap.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.icon_label.setFixedSize(size + 16, size + 16)
        self.setMaximumSize(int(size * 2.2), int(size * 2.8))

    def paintEvent(self, event):
        """Draw subtle card background."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(1, 1, -1, -1)
        painter.setBrush(self.qt_pop.style.get_colour('bg'))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rect, 8, 8)
        super().paintEvent(event)


from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox,
    QPushButton, QSpinBox, QFrame, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
import os


class IconBrowserWidget(QWidget):
    def __init__(self, qt_pop, parent=None, images_path="resources/images"):
        super().__init__(parent)
        self.qt_pop = qt_pop
        self.parent = parent

        if os.path.isdir(images_path):
            IconManager.set_images_path(images_path)

        self.all_icons = IconManager.list_icons()
        self.current_icons = self.all_icons
        self.current_color = self.qt_pop.style.get_colour("accent")
        self.icon_size = 60  # ✅ default icon size

        # ---------- Layout ----------
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)

        # --- Top Controls ---
        top_bar = QHBoxLayout()
        top_bar.setSpacing(8)

        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search icons...")
        self.search_box.textChanged.connect(self._on_search)
        top_bar.addWidget(self.search_box, stretch=2)

        # Color selector
        self.color_combo = QComboBox()
        for name, hex_code in self.qt_pop.style.colour_map().items():
            self.color_combo.addItem(name, hex_code)
        self.color_combo.currentTextChanged.connect(self._on_color_change)
        top_bar.addWidget(self.color_combo)

        # Icon size selector
        self.size_spin = QSpinBox()
        self.size_spin.setRange(16, 128)
        self.size_spin.setValue(self.icon_size)
        self.size_spin.setPrefix("Size: ")
        self.size_spin.valueChanged.connect(self._on_size_change)
        top_bar.addWidget(self.size_spin)

        # Refresh button
        self.refresh_btn = QPushButton("")
        self.refresh_btn.setFixedWidth(40)
        self.refresh_btn.setIcon(
            self.qt_pop.icon.get_pixmap(
                "navigation refresh",
                self.qt_pop.style.get_colour("accent_d3")
            )
        )
        self.refresh_btn.clicked.connect(self._on_refresh)
        top_bar.addWidget(self.refresh_btn)

        main_layout.addLayout(top_bar)

        # --- Separator ---
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separator)

        # --- Icon View (QListWidget) ---
        # --- Icon View (QListWidget) ---
        self.list_widget = QListWidget()
        self.list_widget.setViewMode(QListWidget.IconMode)
        self.list_widget.setResizeMode(QListWidget.Adjust)
        self.list_widget.setWrapping(True)
        self.list_widget.setSpacing(20)  # ✅ more spacing
        self.list_widget.setMovement(QListWidget.Static)
        self.list_widget.setUniformItemSizes(False)  # ✅ allow variable height
        self.list_widget.setWordWrap(True)  # ✅ allow text wrapping
        self.list_widget.setVerticalScrollMode(QListWidget.ScrollPerPixel)
        self.list_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.list_widget.setIconSize(QSize(self.icon_size, self.icon_size))

        main_layout.addWidget(self.list_widget)
        self.setLayout(main_layout)

        # populate icons initially
        self._populate_icons()

    # -------------------------------
    # Populate Icons
    # -------------------------------
    def _populate_icons(self):
        self.list_widget.clear()
        if not self.current_icons:
            item = QListWidgetItem("No icons found")
            self.list_widget.addItem(item)
            return

        self.list_widget.setIconSize(QSize(self.icon_size, self.icon_size))  # ✅ ensure correct icon size

        for icon_name in self.current_icons:
            pixmap = IconManager.get_pixmap(icon_name, self.current_color, size=self.icon_size)
            icon = QIcon(pixmap)
            item = QListWidgetItem(icon, icon_name)
            item.setSizeHint(QSize(self.icon_size + 60, self.icon_size + 60))
            item.setTextAlignment(Qt.AlignHCenter | Qt.AlignTop)
            self.list_widget.addItem(item)

    # -------------------------------
    # Handlers
    # -------------------------------
    def _on_search(self, text: str):
        self.current_icons = IconManager.search_icons(text, self.all_icons)
        self._populate_icons()

    def _on_color_change(self, key: str):
        color_map = self.qt_pop.style.colour_map()
        self.current_color = color_map[key].name()
        self._populate_icons()

    def _on_size_change(self, val: int):
        """Update icon and item size dynamically"""
        self.icon_size = val
        self.list_widget.setIconSize(QSize(val, val))  # ✅ updates the QListWidget view
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item.setSizeHint(QSize(val + 40, val + 50))  # ✅ adjust the visual space
        self._populate_icons()  # ✅ reload icons with new pixmaps

    def _on_refresh(self):
        IconManager.clear_cache()
        self.all_icons = IconManager.list_icons()
        self._populate_icons()




# For testing
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    w = IconBrowserWidget(images_path="resources/images")
    w.resize(1000, 650)
    w.show()
    sys.exit(app.exec())
