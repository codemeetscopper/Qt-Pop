from __future__ import annotations

from typing import Dict, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QMainWindow, QSizePolicy,
    QStackedWidget, QVBoxLayout, QWidget,
)

from nova.ui.sidebar import Sidebar


class PageHeader(QWidget):
    """Fixed-height header bar showing the current page title."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("PageHeader")
        self.setFixedHeight(52)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 0, 24, 0)

        self._title = QLabel("Home")
        self._title.setObjectName("PageHeaderTitle")
        layout.addWidget(self._title)
        layout.addStretch()

    def set_title(self, title: str):
        self._title.setText(title)


class MainWindow(QMainWindow):
    """
    Nova main window.

    Layout:
        Horizontal: Sidebar | (PageHeader / QStackedWidget)
    """

    def __init__(self, qt_pop, plugin_manager, parent: QWidget | None = None):
        super().__init__(parent)
        self._qt_pop = qt_pop
        self._pm = plugin_manager
        self._pages: Dict[str, tuple[str, QWidget]] = {}   # id -> (title, widget)
        self._current: Optional[str] = None

        self.setWindowTitle("Nova")
        self.setObjectName("NovaMainWindow")

        # ── Central widget ────────────────────────────────────
        central = QWidget()
        central.setObjectName("CentralWidget")
        self.setCentralWidget(central)

        h_layout = QHBoxLayout(central)
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.setSpacing(0)

        # Sidebar
        self._sidebar = Sidebar()
        self._sidebar.item_clicked.connect(self.navigate)
        h_layout.addWidget(self._sidebar)

        # Content area
        content = QWidget()
        content.setObjectName("ContentArea")
        content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        v_layout = QVBoxLayout(content)
        v_layout.setContentsMargins(0, 0, 0, 0)
        v_layout.setSpacing(0)

        self._header = PageHeader()
        self._stack = QStackedWidget()
        self._stack.setObjectName("PageStack")

        v_layout.addWidget(self._header)
        v_layout.addWidget(self._stack, 1)

        h_layout.addWidget(content, 1)

    # ──────────────────────────────────────────────────────────
    #  Public API
    # ──────────────────────────────────────────────────────────

    def add_page(self, page_id: str, title: str, icon: str, widget: QWidget):
        """Register a page and add it to the sidebar + stack."""
        self._pages[page_id] = (title, widget)
        self._stack.addWidget(widget)
        self._sidebar.add_item(page_id, title, icon)

    def add_separator(self):
        self._sidebar.add_separator()

    def navigate(self, page_id: str):
        if page_id not in self._pages:
            return
        title, widget = self._pages[page_id]
        self._stack.setCurrentWidget(widget)
        self._header.set_title(title)
        self._sidebar.set_active(page_id)
        self._current = page_id

    def current_page(self) -> Optional[str]:
        return self._current

    def closeEvent(self, event):
        self._pm.stop_all()
        super().closeEvent(event)
