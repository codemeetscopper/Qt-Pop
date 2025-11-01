from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QFrame, QApplication
)
from PySide6.QtGui import QColor, QPainter, QBrush, QPen, QFont
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Property
import sys


def contrast_color(color: QColor) -> QColor:
    """Return white or black for best contrast with the given color."""
    brightness = (color.red() * 299 + color.green() * 587 + color.blue() * 114) / 1000
    return QColor(0, 0, 0) if brightness > 128 else QColor(255, 255, 255)


class ColorCard(QFrame):
    """Rounded Material color card with internal text and hover highlight."""
    def __init__(self, color: QColor, tag: str, hex_str: str, height: int = 60, parent=None):
        super().__init__(parent)
        self._color = color
        self._tag = tag
        self._hex_str = hex_str
        self._radius = 10
        self._hover_opacity = 0.0
        self._border_alpha = 40
        # self.setFixedHeight(height)
        # self.setMinimumWidth(240)

        # Animation for hover
        self._hover_anim = QPropertyAnimation(self, b"hover_opacity", self)
        self._hover_anim.setDuration(180)
        self._hover_anim.setEasingCurve(QEasingCurve.OutQuad)

    # --- Hover events ---
    def enterEvent(self, event):
        self._hover_anim.stop()
        self._hover_anim.setEndValue(0.12)
        self._hover_anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hover_anim.stop()
        self._hover_anim.setEndValue(0.0)
        self._hover_anim.start()
        super().leaveEvent(event)

    # --- Painting ---
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(0, 0, -1, -1)

        # Base color
        painter.setBrush(QBrush(self._color))
        painter.setPen(QPen(QColor(0, 0, 0, self._border_alpha)))
        painter.drawRoundedRect(rect, self._radius, self._radius)

        # Hover overlay
        if self._hover_opacity > 0:
            overlay = QColor(0, 0, 0)
            overlay.setAlphaF(self._hover_opacity)
            painter.setBrush(QBrush(overlay))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(rect, self._radius, self._radius)

        # Text
        painter.setPen(contrast_color(self._color))
        tag_font = QFont("Segoe UI", 10, QFont.DemiBold)
        hex_font = QFont("Segoe UI", 9)

        painter.setFont(tag_font)
        painter.drawText(rect.adjusted(12, 8, -8, -8), Qt.AlignLeft | Qt.AlignTop, self._tag)

        painter.setFont(hex_font)
        painter.drawText(rect.adjusted(8, 8, -12, -10), Qt.AlignRight | Qt.AlignBottom, self._hex_str.upper())

    # --- Property for animation ---
    def get_hover_opacity(self): return self._hover_opacity
    def set_hover_opacity(self, val):
        self._hover_opacity = val
        self.update()
    hover_opacity = Property(float, get_hover_opacity, set_hover_opacity)

    def set_color(self, color: QColor, tag=None, hex_str=None):
        self._color = color
        if tag:
            self._tag = tag
        if hex_str:
            self._hex_str = hex_str
        self.update()


class ColorDisplayWidget(QWidget):
    """Flat horizontal Material color display (single-line)."""
    def __init__(self, color_hex="#2196F3", color_tag="Primary", parent=None):
        super().__init__(parent)

        self._color = QColor(color_hex)
        self._tag = color_tag

        # Only one element now — no outer hover box
        self.card = ColorCard(self._color, self._tag, self._color.name())

        layout = QHBoxLayout(self)
        layout.addWidget(self.card)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

    def set_color(self, color_hex: str, tag: str = None):
        self._color = QColor(color_hex)
        if tag:
            self._tag = tag
        self.card.set_color(self._color, self._tag, self._color.name())


# --- Demo ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = QWidget()
    layout = QHBoxLayout(w)

    colors = [
        ("#2196F3", "Primary"),
        ("#4CAF50", "Success"),
        ("#F44336", "Error"),
        ("#FFC107", "Warning"),
        ("#9C27B0", "Accent"),
    ]
    for hex_val, tag in colors:
        layout.addWidget(ColorDisplayWidget(hex_val, tag))

    w.setWindowTitle("Flat Material Color Cards")
    w.show()
    sys.exit(app.exec())
