"""Custom frameless window title bar integrated with QtPop."""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import QPoint, QRect, Qt
from PySide6.QtGui import QIcon, QMouseEvent, QPainter, QPen
from PySide6.QtWidgets import QHBoxLayout, QLabel, QSizeGrip, QToolButton, QWidget



class CustomTitleBar(QWidget):
    """Stylised title bar that mirrors the active QtPop palette."""

    HEIGHT = 44

    def __init__(
        self,
        qtpop,
        parent: QWidget | None = None,
        *,
        app_icon: Optional[QIcon] = None,
        app_name: str = "QtPop Demo",
    ) -> None:
        super().__init__(parent)
        self.setObjectName("QtPopTitleBar")
        self.setFixedHeight(self.HEIGHT)
        self.setAttribute(Qt.WA_StyledBackground, True)

        self._qtpop = qtpop
        self._window = parent
        self._drag_position = QPoint()
        self._drag_active = False

        self._icon_label = QLabel()
        self._icon_label.setObjectName("TitleIcon")
        self._icon_label.setFixedSize(32, 32)

        self._title_label = QLabel(app_name)
        self._title_label.setObjectName("TitleText")

        self._menu_button = QToolButton()
        self._menu_button.setObjectName("TitleMenuButton")
        self._menu_button.setAutoRaise(True)

        self._minimise_button = self._make_control_button("navigation minimize")
        self._maximise_button = self._make_control_button("navigation fullscreen")
        self._close_button = self._make_control_button("navigation close")

        self._minimise_button.clicked.connect(self._minimise)
        self._maximise_button.clicked.connect(self._toggle_maximise)
        self._close_button.clicked.connect(self._close)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(12)
        layout.addWidget(self._icon_label, alignment=Qt.AlignVCenter)
        layout.addWidget(self._title_label, 1, alignment=Qt.AlignVCenter | Qt.AlignLeft)
        layout.addWidget(self._menu_button, alignment=Qt.AlignVCenter)
        layout.addWidget(self._minimise_button, alignment=Qt.AlignVCenter)
        layout.addWidget(self._maximise_button, alignment=Qt.AlignVCenter)
        layout.addWidget(self._close_button, alignment=Qt.AlignVCenter)

        self._grips = [QSizeGrip(self) for _ in range(4)]
        for grip in self._grips:
            grip.setVisible(False)

        self._menu_button.setCursor(Qt.PointingHandCursor)
        self._minimise_button.setCursor(Qt.PointingHandCursor)
        self._maximise_button.setCursor(Qt.PointingHandCursor)
        self._close_button.setCursor(Qt.PointingHandCursor)

        self._set_icon(app_icon)
        self.refresh_palette()

    # ------------------------------------------------------------------
    # Palette helpers
    # ------------------------------------------------------------------
    def refresh_palette(self) -> None:
        """Update the button icons and label colours from the active palette."""
        accent = self._qtpop.style.get_colour("accent")
        foreground = self._qtpop.style.get_colour("fg1")

        self._title_label.setStyleSheet(f"color: {accent};")
        self._menu_button.setIcon(self._render_icon("action info", foreground, 20))
        self._minimise_button.setIcon(self._render_icon("navigation minimize", foreground, 20))
        self._close_button.setIcon(self._render_icon("navigation close", foreground, 20))

        if self._window and self._window.isMaximized():
            icon_name = "navigation fullscreen exit"
        else:
            icon_name = "navigation fullscreen"
        self._maximise_button.setIcon(self._render_icon(icon_name, foreground, 20))

    # ------------------------------------------------------------------
    # Base helpers
    # ------------------------------------------------------------------
    def _set_icon(self, icon: Optional[QIcon]) -> None:
        if icon is not None:
            pixmap = icon.pixmap(32, 32)
        else:
            pixmap = self._render_pixmap("action join left", self._qtpop.style.get_colour("accent"), 32)
        if pixmap:
            self._icon_label.setPixmap(pixmap)

    def _make_control_button(self, icon_name: str) -> QToolButton:
        button = QToolButton()
        button.setObjectName("TitleControlButton")
        button.setAutoRaise(True)
        button.setIcon(self._render_icon(icon_name, self._qtpop.style.get_colour("fg1"), 20))
        return button

    def _render_icon(self, name: str, colour: str, size: int) -> QIcon:
        pixmap = self._render_pixmap(name, colour, size)
        return QIcon(pixmap) if pixmap else QIcon()

    def _render_pixmap(self, name: str, colour: str, size: int):
        try:
            return self._qtpop.icon.get_pixmap(name, colour, size)
        except Exception:
            return None

    # ------------------------------------------------------------------
    # Window controls
    # ------------------------------------------------------------------
    def _minimise(self) -> None:
        if self._window:
            self._window.showMinimized()

    def _toggle_maximise(self) -> None:
        if not self._window:
            return
        if self._window.isMaximized():
            self._window.showNormal()
        else:
            self._window.showMaximized()
        self.refresh_palette()

    def _close(self) -> None:
        if self._window:
            self._window.close()

    # ------------------------------------------------------------------
    # Mouse handling for drag
    # ------------------------------------------------------------------
    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton and self._window:
            self._drag_active = True
            self._drag_position = event.globalPosition().toPoint() - self._window.frameGeometry().topLeft()
            event.accept()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._drag_active and event.buttons() & Qt.LeftButton and self._window:
            self._window.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self._drag_active = False
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self._toggle_maximise()
        super().mouseDoubleClickEvent(event)

    # ------------------------------------------------------------------
    # Resize grip layout
    # ------------------------------------------------------------------
    def resizeEvent(self, event) -> None:  # type: ignore[override]
        super().resizeEvent(event)
        if not self._window:
            return
        grip_size = 16
        rect = self._window.rect()
        self._grips[0].setGeometry(QRect(rect.left(), rect.top(), grip_size, grip_size))
        self._grips[1].setGeometry(QRect(rect.right() - grip_size, rect.top(), grip_size, grip_size))
        self._grips[2].setGeometry(QRect(rect.left(), rect.bottom() - grip_size, grip_size, grip_size))
        self._grips[3].setGeometry(QRect(rect.right() - grip_size, rect.bottom() - grip_size, grip_size, grip_size))

    # ------------------------------------------------------------------
    # Painting
    # ------------------------------------------------------------------
    def paintEvent(self, event) -> None:  # type: ignore[override]
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        accent = self._qtpop.style.get_colour("neutral_l2")
        painter.setPen(QPen(accent))
        painter.drawLine(0, self.height() - 1, self.width(), self.height() - 1)
        painter.end()

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------
    def nativeEvent(self, eventType, message):  # pragma: no cover - platform specific
        if eventType == b"windows_generic_MSG" and self._window:
            from ctypes import windll
            if windll.user32.IsZoomed(int(self._window.winId())):
                for grip in self._grips:
                    grip.setVisible(False)
            else:
                for grip in self._grips:
                    grip.setVisible(True)
        return super().nativeEvent(eventType, message)
