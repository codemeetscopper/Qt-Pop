from __future__ import annotations

from typing import Dict, Optional

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton, QScrollArea,
    QSizePolicy, QVBoxLayout, QWidget,
)

EXPANDED = 240
COLLAPSED = 64
ANIM_MS = 200

# Horizontal padding on each side when collapsed so the icon is centred in 64px.
# icon_width=28, padding = (64 - 28) / 2 = 18
_COLLAPSED_PAD = (COLLAPSED - 28) // 2


def _accent_color() -> str:
    """Retrieve accent hex from StyleManager if available, fall back to a safe default."""
    try:
        from qtpop.appearance.stylemanager import StyleManager
        return StyleManager.get_colour("accent")
    except Exception:
        return "#0088CC"


def _fg1_color() -> str:
    try:
        from qtpop.appearance.stylemanager import StyleManager
        return StyleManager.get_colour("fg1")
    except Exception:
        return "#444444"


def _get_icon_pixmap(icon_name: str, color: str, size: int = 28) -> Optional[QPixmap]:
    """Return a coloured pixmap for icon_name, or None on failure."""
    try:
        from qtpop.appearance.iconmanager import IconManager
        return IconManager.get_pixmap(icon_name, color, size)
    except Exception:
        return None


class SidebarItem(QWidget):
    """A single navigation row — icon + optional label."""

    clicked = Signal(str)   # item id

    def __init__(self, item_id: str, label: str, icon_name: str,
                 parent: QWidget | None = None):
        super().__init__(parent)
        self._id = item_id
        self._label_text = label
        self._icon_name = icon_name
        self._active = False

        self.setObjectName("SidebarItem")
        self.setFixedHeight(48)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setCursor(Qt.PointingHandCursor)

        self._layout = QHBoxLayout(self)
        # Use 18px left margin to center the 28px icon at 32px (same as collapsed state)
        self._layout.setContentsMargins(18, 0, 12, 0)
        self._layout.setSpacing(16)

        # Icon — pixmap if IconManager has it, otherwise plain text
        self._icon = QLabel()
        self._icon.setObjectName("SidebarItemIcon")
        self._icon.setFixedSize(28, 28)
        self._icon.setAlignment(Qt.AlignCenter)
        self._icon.setScaledContents(True)

        self._text = QLabel(label)
        self._text.setObjectName("SidebarItemText")
        self._text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self._text.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        self._layout.addWidget(self._icon)
        self._layout.addWidget(self._text)

        self._apply_inactive_style()

    # ──────────────────────────────────────────────────────
    #  Public API
    # ──────────────────────────────────────────────────────

    def set_text_visible(self, visible: bool):
        self._text.setVisible(visible)
        if visible:
            self._layout.setContentsMargins(18, 0, 12, 0)
            self.setToolTip("")
        else:
            # Centre the 28px icon within 64px by using equal side margins
            self._layout.setContentsMargins(_COLLAPSED_PAD, 0, _COLLAPSED_PAD, 0)
            self.setToolTip(self._label_text)

    def set_active(self, active: bool):
        if self._active == active:
            return
        self._active = active
        # Update the container's QSS property (drives background + border)
        self.setProperty("active", active)
        self.style().unpolish(self)
        self.style().polish(self)
        # Directly update child label colours because Qt QSS does not reliably
        # resolve dynamic-property selectors on descendant widgets.
        if active:
            self._apply_active_style()
        else:
            self._apply_inactive_style()
        self.update()

    def is_active(self) -> bool:
        return self._active

    # ──────────────────────────────────────────────────────
    #  Internal
    # ──────────────────────────────────────────────────────

    def _set_icon_pixmap(self, color: str):
        """Set the icon QLabel pixmap with the requested colour."""
        # Check for inline SVG
        clean_name = self._icon_name.strip()
        if clean_name.startswith("<") and "svg" in clean_name:
            try:
                from PySide6.QtCore import QByteArray
                from PySide6.QtSvg import QSvgRenderer
                from PySide6.QtGui import QColor, QPainter, QPixmap
                
                # Render SVG to pixmap
                qbytearray = QByteArray(clean_name.encode("utf-8"))
                renderer = QSvgRenderer(qbytearray)
                
                if renderer.isValid():
                    size = 28
                    px = QPixmap(size, size)
                    px.fill(Qt.transparent)
                    painter = QPainter(px)
                    renderer.render(painter)
                    painter.end()
                    
                    # Recolor
                    colored_px = QPixmap(size, size)
                    colored_px.fill(Qt.transparent)
                    painter = QPainter(colored_px)
                    painter.setRenderHint(QPainter.Antialiasing)
                    painter.setRenderHint(QPainter.SmoothPixmapTransform)
                    # Draw the color
                    painter.fillRect(colored_px.rect(), QColor(color))
                    # Apply the icon as a mask
                    painter.setCompositionMode(QPainter.CompositionMode_DestinationIn)
                    painter.drawPixmap(0, 0, px)
                    painter.end()
                    
                    self._icon.setPixmap(colored_px)
                    self._icon.setStyleSheet("background: transparent;")
                    return
            except Exception:
                pass  # Fallback to standard handling

        px = _get_icon_pixmap(self._icon_name, color)
        if px is not None and not px.isNull():
            self._icon.setPixmap(px)
            self._icon.setStyleSheet("background: transparent;")
        else:
            # Fallback: show icon_name as text IF it's short
            if len(self._icon_name) < 20:
                self._icon.setText(self._icon_name)
                self._icon.setStyleSheet(f"color: {color}; background: transparent;")
            else:
                # If it's a long string (broken SVG), show a placeholder or empty
                # Here we just show a generic character or nothing
                self._icon.setText("?")
                self._icon.setStyleSheet(f"color: {color}; background: transparent;")

    def _apply_active_style(self):
        ac = _accent_color()
        self._set_icon_pixmap(ac)
        self._text.setStyleSheet(
            f"color: {ac}; font-weight: 600; background: transparent;"
        )

    def _apply_inactive_style(self):
        fg = _fg1_color()
        self._set_icon_pixmap(fg)
        self._text.setStyleSheet(f"color: {fg}; background: transparent;")

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.clicked.emit(self._id)


class SidebarSeparator(QFrame):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("SidebarSeparator")
        self.setFrameShape(QFrame.HLine)
        self.setFixedHeight(1)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)


class Sidebar(QFrame):
    """
    Collapsible hamburger sidebar.

    Layout (top-to-bottom in nav area):
      [standard items]
      [plugin items]  ← inserted before separator
      [separator]
      [settings / about items]
      [stretch]

    Signals:
        item_clicked(str)   emitted with the page id when a nav item is clicked
    """

    item_clicked = Signal(str)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self._expanded = True
        self._items: Dict[str, SidebarItem] = {}
        self._separator: Optional[SidebarSeparator] = None

        self.setMinimumWidth(EXPANDED)
        self.setMaximumWidth(EXPANDED)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header ──────────────────────────────────────────
        header = QWidget()
        header.setObjectName("SidebarHeader")
        header.setFixedHeight(56)
        h_layout = QHBoxLayout(header)
        # Use 12px left margin to center the 40px button at 32px (32 - 20 = 12)
        h_layout.setContentsMargins(12, 0, 8, 0)
        h_layout.setSpacing(8)

        self._hamburger = QPushButton()
        self._hamburger.setObjectName("HamburgerButton")
        self._hamburger.setFixedSize(40, 40)
        self._hamburger.setCursor(Qt.PointingHandCursor)
        self._hamburger.clicked.connect(self.toggle)
        # Apply menu icon
        self._set_hamburger_icon()

        self._logo = QLabel("Nova")
        self._logo.setObjectName("SidebarLogo")

        h_layout.addWidget(self._hamburger)
        h_layout.addWidget(self._logo)
        h_layout.addStretch()
        root.addWidget(header)

        # ── Scroll area ──────────────────────────────────────
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

        # ── Animations ───────────────────────────────────────
        self._anim_min = QPropertyAnimation(self, b"minimumWidth")
        self._anim_min.setDuration(ANIM_MS)
        self._anim_min.setEasingCurve(QEasingCurve.InOutCubic)

        self._anim_max = QPropertyAnimation(self, b"maximumWidth")
        self._anim_max.setDuration(ANIM_MS)
        self._anim_max.setEasingCurve(QEasingCurve.InOutCubic)

    # ──────────────────────────────────────────────────────
    #  Public API
    # ──────────────────────────────────────────────────────

    def add_item(self, item_id: str, label: str, icon_name: str) -> SidebarItem:
        """Add a standard navigation item (appended before the trailing stretch)."""
        item = SidebarItem(item_id, label, icon_name)
        item.clicked.connect(self.item_clicked)
        # Insert before the trailing stretch
        self._nav_layout.insertWidget(self._nav_layout.count() - 1, item)
        self._items[item_id] = item
        return item

    def add_plugin_item(self, item_id: str, label: str, icon_name: str) -> SidebarItem:
        """
        Add a plugin navigation item, inserted BEFORE the separator so plugin
        pages appear between the main nav items and settings/about.
        Falls back to add_item behaviour if no separator has been added yet.
        """
        if item_id in self._items:
            return self._items[item_id]

        item = SidebarItem(item_id, label, icon_name)
        item.clicked.connect(self.item_clicked)

        if self._separator is not None:
            idx = self._nav_layout.indexOf(self._separator)
            self._nav_layout.insertWidget(idx, item)
        else:
            self._nav_layout.insertWidget(self._nav_layout.count() - 1, item)

        self._items[item_id] = item

        # If sidebar is collapsed, hide text immediately
        if not self._expanded:
            item.set_text_visible(False)

        return item

    def remove_item(self, item_id: str):
        """Remove a navigation item (e.g. when a plugin is de-favorited or deleted)."""
        item = self._items.pop(item_id, None)
        if item is not None:
            self._nav_layout.removeWidget(item)
            item.setParent(None)
            item.deleteLater()

    def add_separator(self):
        """Add a horizontal divider. The first separator is used as the plugin insertion point."""
        sep = SidebarSeparator()
        self._nav_layout.insertWidget(self._nav_layout.count() - 1, sep)
        if self._separator is None:
            self._separator = sep

    def set_active(self, item_id: str):
        for sid, item in self._items.items():
            item.set_active(sid == item_id)

    def toggle(self):
        if self._expanded:
            self._collapse()
        else:
            self._expand()

    # ──────────────────────────────────────────────────────
    #  Internal
    # ──────────────────────────────────────────────────────

    def _set_hamburger_icon(self):
        """Set hamburger button icon via IconManager, fall back to text."""
        px = _get_icon_pixmap("navigation_menu", _fg1_color(), 28)
        if px is not None and not px.isNull():
            self._hamburger.setIcon(px)
            self._hamburger.setIconSize(px.size())
            self._hamburger.setText("")
        else:
            self._hamburger.setText("☰")

    def _expand(self):
        self._expanded = True
        self._logo.setVisible(True)
        for item in self._items.values():
            item.set_text_visible(True)
        self._animate(self.width(), EXPANDED)

    def _collapse(self):
        self._expanded = False
        self._logo.setVisible(False)
        for item in self._items.values():
            item.set_text_visible(False)
        self._animate(self.width(), COLLAPSED)

    def _animate(self, start: int, end: int):
        for anim in (self._anim_min, self._anim_max):
            anim.stop()
            anim.setStartValue(start)
            anim.setEndValue(end)
            anim.start()
