from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame, QApplication
)
from PySide6.QtGui import QColor, QPainter, QBrush, QPen, QFont, QPalette
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Property
import sys


class ColorCard(QFrame):
    """Rounded color preview box (no stylesheets)."""
    def __init__(self, color: QColor, size: int = 56, parent=None):
        super().__init__(parent)
        self._color = color
        self._radius = 8
        self._border_alpha = 40
        self.setFixedSize(size, size)

    def set_color(self, color: QColor):
        self._color = color
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect()

        # Fill color
        brush = QBrush(self._color)
        painter.setBrush(brush)
        pen = QPen(QColor(0, 0, 0, self._border_alpha))
        painter.setPen(pen)
        painter.drawRoundedRect(rect.adjusted(0, 0, -1, -1), self._radius, self._radius)


class ColorDisplayWidget(QWidget):
    """Material-style color display (no stylesheets)."""
    def __init__(self, color_hex=QColor('#ffffff'), color_tag="Primary", parent=None):
        super().__init__(parent)

        # Core data
        self._color = color_hex
        self._tag = color_tag
        self._hover_opacity = 0.0

        # --- Components ---
        self.card = ColorCard(self._color)
        self.tag_label = QLabel(self._tag)
        self.hex_label = QLabel(self._color.name())

        # --- Fonts ---
        tag_font = QFont("Segoe UI", 10, QFont.Bold)
        hex_font = QFont("Segoe UI", 9)
        self.tag_label.setFont(tag_font)
        self.hex_label.setFont(hex_font)

        # Use palette-based coloring
        pal = self.palette()
        self.tag_label.setPalette(pal)
        self.hex_label.setPalette(pal)

        # --- Layout ---
        text_layout = QVBoxLayout()
        text_layout.addWidget(self.tag_label)
        text_layout.addWidget(self.hex_label)
        text_layout.setSpacing(2)

        main_layout = QHBoxLayout(self)
        main_layout.addWidget(self.card)
        main_layout.addLayout(text_layout)
        main_layout.addStretch()
        main_layout.setContentsMargins(12, 8, 12, 8)
        main_layout.setSpacing(12)

        # --- Animation ---
        self._hover_anim = QPropertyAnimation(self, b"hover_opacity", self)
        self._hover_anim.setDuration(200)
        self._hover_anim.setEasingCurve(QEasingCurve.OutQuad)

    # --- Hover effect ---
    def enterEvent(self, event):
        self._hover_anim.stop()
        self._hover_anim.setEndValue(0.08)
        self._hover_anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hover_anim.stop()
        self._hover_anim.setEndValue(0.0)
        self._hover_anim.start()
        super().leaveEvent(event)

    # --- Paint background hover ---
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        if self._hover_opacity > 0:
            bg_color = self.palette().color(QPalette.WindowText)
            bg_color.setAlphaF(self._hover_opacity)
            painter.setBrush(QBrush(bg_color))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(self.rect(), 10, 10)
        super().paintEvent(event)

    # --- Property for animation ---
    def get_hover_opacity(self): return self._hover_opacity
    def set_hover_opacity(self, val):
        self._hover_opacity = val
        self.update()
    hover_opacity = Property(float, get_hover_opacity, set_hover_opacity)

    # --- Update color dynamically ---
    def set_color(self, color_hex: str, tag: str = None):
        self._color = QColor(color_hex)
        if tag:
            self._tag = tag
        self.card.set_color(self._color)
        self.hex_label.setText(color_hex)
        self.tag_label.setText(self._tag)
        self.update()


# --- Demo Application ---
if __name__ == "__main__":
    app = QApplication(sys.argv)

    from PySide6.QtWidgets import QVBoxLayout, QWidget

    root = QWidget()
    layout = QVBoxLayout(root)
    layout.setSpacing(8)
    layout.setContentsMargins(20, 20, 20, 20)

    layout.addWidget(ColorDisplayWidget("#6200EE", "Primary"))
    layout.addWidget(ColorDisplayWidget("#03DAC6", "Secondary"))
    layout.addWidget(ColorDisplayWidget("#B00020", "Error"))
    layout.addWidget(ColorDisplayWidget("#018786", "Teal"))
    layout.addStretch()

    root.setWindowTitle("Material Color Display Widget")
    root.resize(320, 320)
    root.show()

    sys.exit(app.exec())
