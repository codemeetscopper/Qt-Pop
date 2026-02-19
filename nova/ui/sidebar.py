from __future__ import annotations

from typing import Callable, Dict, Optional

from PySide6.QtCore import (
    QEasingCurve, QPropertyAnimation, Qt, Signal,
)
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton, QScrollArea,
    QSizePolicy, QVBoxLayout, QWidget,
)

EXPANDED = 240
COLLAPSED = 64
ANIM_MS = 200


class SidebarItem(QWidget):
    """A single navigation item with icon + label."""

    clicked = Signal(str)  # item id

    def __init__(self, item_id: str, label: str, icon_label: str,
                 parent: QWidget | None = None):
        super().__init__(parent)
        self._id = item_id
        self._label_text = label
        self._active = False

        self.setObjectName("SidebarItem")
        self.setFixedHeight(44)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip(label)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(12)

        self._icon = QLabel(icon_label)
        self._icon.setObjectName("SidebarItemIcon")
        self._icon.setFixedSize(20, 20)
        self._icon.setAlignment(Qt.AlignCenter)

        self._text = QLabel(label)
        self._text.setObjectName("SidebarItemText")
        self._text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        layout.addWidget(self._icon)
        layout.addWidget(self._text)

    def set_text_visible(self, visible: bool):
        self._text.setVisible(visible)
        if visible:
            self.setToolTip("")
        else:
            self.setToolTip(self._label_text)

    def set_active(self, active: bool):
        if self._active == active:
            return
        self._active = active
        self.setProperty("active", active)
        # Force QSS re-evaluation
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def is_active(self) -> bool:
        return self._active

    def mousePressEvent(self, event):
        self.clicked.emit(self._id)
        super().mousePressEvent(event)


class SidebarSeparator(QFrame):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("SidebarSeparator")
        self.setFrameShape(QFrame.HLine)
        self.setFixedHeight(1)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)


class Sidebar(QFrame):
    """
    Collapsible hamburger sidebar navigation.

    Signals:
        item_clicked(str)  — emitted with the page id
    """

    item_clicked = Signal(str)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self._expanded = True
        self._items: Dict[str, SidebarItem] = {}

        self.setFixedWidth(EXPANDED)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header ──────────────────────────────────────────────
        header = QWidget()
        header.setObjectName("SidebarHeader")
        header.setFixedHeight(56)
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(8, 0, 8, 0)
        h_layout.setSpacing(8)

        self._hamburger = QPushButton("☰")
        self._hamburger.setObjectName("HamburgerButton")
        self._hamburger.setFixedSize(40, 40)
        self._hamburger.setCursor(Qt.PointingHandCursor)
        self._hamburger.clicked.connect(self.toggle)

        self._logo = QLabel("Nova")
        self._logo.setObjectName("SidebarLogo")

        h_layout.addWidget(self._hamburger)
        h_layout.addWidget(self._logo)
        h_layout.addStretch()
        root.addWidget(header)

        # ── Scroll area for nav items ────────────────────────────
        scroll = QScrollArea()
        scroll.setObjectName("SidebarScroll")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setFrameShape(QFrame.NoFrame)

        self._nav_container = QWidget()
        self._nav_layout = QVBoxLayout(self._nav_container)
        self._nav_layout.setContentsMargins(4, 8, 4, 8)
        self._nav_layout.setSpacing(2)
        self._nav_layout.addStretch()

        scroll.setWidget(self._nav_container)
        root.addWidget(scroll, 1)

        # ── Animation ───────────────────────────────────────────
        self._anim_min = QPropertyAnimation(self, b"minimumWidth")
        self._anim_min.setDuration(ANIM_MS)
        self._anim_min.setEasingCurve(QEasingCurve.InOutCubic)
        self._anim_max = QPropertyAnimation(self, b"maximumWidth")
        self._anim_max.setDuration(ANIM_MS)
        self._anim_max.setEasingCurve(QEasingCurve.InOutCubic)

    # ──────────────────────────────────────────────────────────
    #  Public API
    # ──────────────────────────────────────────────────────────

    def add_item(self, item_id: str, label: str, icon_label: str) -> SidebarItem:
        item = SidebarItem(item_id, label, icon_label)
        item.clicked.connect(self.item_clicked)
        # Insert before the trailing stretch (last item)
        count = self._nav_layout.count()
        self._nav_layout.insertWidget(count - 1, item)
        self._items[item_id] = item
        return item

    def add_separator(self):
        sep = SidebarSeparator()
        count = self._nav_layout.count()
        self._nav_layout.insertWidget(count - 1, sep)

    def set_active(self, item_id: str):
        for sid, item in self._items.items():
            item.set_active(sid == item_id)

    def toggle(self):
        if self._expanded:
            self._collapse()
        else:
            self._expand()

    # ──────────────────────────────────────────────────────────
    #  Internal
    # ──────────────────────────────────────────────────────────

    def _expand(self):
        self._expanded = True
        self._logo.setVisible(True)
        for item in self._items.values():
            item.set_text_visible(True)
        self._animate(COLLAPSED, EXPANDED)

    def _collapse(self):
        self._expanded = False
        self._logo.setVisible(False)
        for item in self._items.values():
            item.set_text_visible(False)
        self._animate(EXPANDED, COLLAPSED)

    def _animate(self, start: int, end: int):
        for anim in (self._anim_min, self._anim_max):
            anim.stop()
            anim.setStartValue(start)
            anim.setEndValue(end)
            anim.start()
