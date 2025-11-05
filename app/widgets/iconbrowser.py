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



class IconBrowserWidget(QWidget):
    def __init__(self, qt_pop: QtPop, parent=None, images_path="resources/images"):
        super().__init__(parent)
        self.qt_pop = qt_pop

        if os.path.isdir(images_path):
            IconManager.set_images_path(images_path)

        self.all_icons = IconManager.list_icons()
        self.current_icons = self.all_icons
        self.current_color = self.qt_pop.style.get_colour("accent")
        self.icon_size = 48

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
        colours = self.qt_pop.style.colour_map()
        for name, hex_code in colours.items():
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
        self.refresh_btn = QPushButton("⟳")
        self.refresh_btn.setFixedWidth(40)
        self.refresh_btn.clicked.connect(self._on_refresh)
        top_bar.addWidget(self.refresh_btn)

        main_layout.addLayout(top_bar)

        # --- Separator ---
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separator)

        # --- Scrollable grid for icons ---
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        self.scroll_content = QWidget()
        self.grid_layout = QGridLayout(self.scroll_content)
        self.grid_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.grid_layout.setSpacing(10)

        self.scroll_area.setWidget(self.scroll_content)
        main_layout.addWidget(self.scroll_area)
        self.setLayout(main_layout)

        self._populate_icons()

    # -------------------------------
    # UI Interaction Logic
    # -------------------------------

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._populate_icons()

    def _populate_icons(self):
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        if not self.current_icons:
            lbl = QLabel("No icons found.")
            lbl.setAlignment(Qt.AlignCenter)
            self.grid_layout.addWidget(lbl, 0, 0)
            return

        # Compute columns dynamically based on available width
        available_width = self.scroll_area.viewport().width()
        card_width = self.icon_size + 40  # estimate per card including spacing
        cols = max(1, available_width // card_width)

        for i, icon_name in enumerate(self.current_icons):
            pixmap = IconManager.get_pixmap(icon_name, self.current_color, size=self.icon_size)
            card = IconCardWidget(icon_name, pixmap, self.qt_pop)
            card.update_icon(pixmap, self.icon_size)
            row, col = divmod(i, cols)
            self.grid_layout.addWidget(card, row, col)

    def _on_search(self, text: str):
        self.current_icons = IconManager.search_icons(text, self.all_icons)
        self._populate_icons()

    def _on_color_change(self, key: str):
        color_map = self.qt_pop.style.colour_map()
        self.current_color = color_map[key].name()
        self._populate_icons()

    def _on_size_change(self, val: int):
        self.icon_size = val
        self._populate_icons()

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
