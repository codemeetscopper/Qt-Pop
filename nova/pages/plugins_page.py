from __future__ import annotations

from typing import Dict, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame, QGridLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QSizePolicy, QVBoxLayout, QWidget,
)


class PluginCard(QFrame):
    """
    Card representing a single plugin with status indicator and start/stop controls.
    """

    start_clicked = Signal(str)     # plugin_id
    stop_clicked = Signal(str)      # plugin_id
    view_clicked = Signal(str)      # plugin_id

    def __init__(self, manifest, plugin_manager, parent: QWidget | None = None):
        super().__init__(parent)
        self._manifest = manifest
        self._pm = plugin_manager
        self._active = False

        self.setObjectName("PluginCard")
        self.setFrameShape(QFrame.StyledPanel)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        v = QVBoxLayout(self)
        v.setContentsMargins(20, 20, 20, 20)
        v.setSpacing(12)

        # ── Header row ─────────────────────────────────────────
        header_row = QHBoxLayout()
        header_row.setSpacing(10)

        self._status_dot = QLabel("●")
        self._status_dot.setObjectName("StatusDotInactive")
        self._status_dot.setFixedSize(12, 12)
        self._status_dot.setAlignment(Qt.AlignCenter)

        name_lbl = QLabel(manifest.name)
        name_lbl.setObjectName("PluginCardName")

        ver_lbl = QLabel(f"v{manifest.version}")
        ver_lbl.setObjectName("PluginCardVersion")

        header_row.addWidget(self._status_dot)
        header_row.addWidget(name_lbl, 1)
        header_row.addWidget(ver_lbl)
        v.addLayout(header_row)

        # ── Description ────────────────────────────────────────
        desc = QLabel(manifest.description or "No description provided.")
        desc.setObjectName("PluginCardDesc")
        desc.setWordWrap(True)
        v.addWidget(desc)

        author = QLabel(f"by {manifest.author}" if manifest.author else "")
        author.setObjectName("PluginCardAuthor")
        v.addWidget(author)

        # ── Buttons ────────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        self._start_btn = QPushButton("Start")
        self._start_btn.setObjectName("PluginStartButton")
        self._start_btn.setFixedWidth(80)
        self._start_btn.clicked.connect(lambda: self.start_clicked.emit(manifest.id))

        self._stop_btn = QPushButton("Stop")
        self._stop_btn.setObjectName("PluginStopButton")
        self._stop_btn.setFixedWidth(80)
        self._stop_btn.setEnabled(False)
        self._stop_btn.clicked.connect(lambda: self.stop_clicked.emit(manifest.id))

        self._view_btn = QPushButton("View")
        self._view_btn.setObjectName("PluginViewButton")
        self._view_btn.setFixedWidth(80)
        self._view_btn.setEnabled(False)
        self._view_btn.clicked.connect(lambda: self.view_clicked.emit(manifest.id))

        btn_row.addWidget(self._start_btn)
        btn_row.addWidget(self._stop_btn)
        btn_row.addWidget(self._view_btn)
        btn_row.addStretch()
        v.addLayout(btn_row)

    def set_active(self, active: bool):
        self._active = active
        self._start_btn.setEnabled(not active)
        self._stop_btn.setEnabled(active)
        self._view_btn.setEnabled(active)
        self._status_dot.setObjectName("StatusDotActive" if active else "StatusDotInactive")
        self._status_dot.style().unpolish(self._status_dot)
        self._status_dot.style().polish(self._status_dot)

    def set_crashed(self):
        self._status_dot.setObjectName("StatusDotCrashed")
        self._status_dot.style().unpolish(self._status_dot)
        self._status_dot.style().polish(self._status_dot)
        self._start_btn.setEnabled(True)
        self._stop_btn.setEnabled(False)
        self._view_btn.setEnabled(False)


class PluginsPage(QWidget):
    """
    Plugin manager page — shows all discovered/loaded plugins as cards.
    """

    navigate_to_plugin = Signal(str)  # plugin_id

    def __init__(self, plugin_manager, parent: QWidget | None = None):
        super().__init__(parent)
        self._pm = plugin_manager
        self._cards: Dict[str, PluginCard] = {}
        self.setObjectName("PluginsPage")

        # Connect plugin manager signals
        self._pm.plugin_started.connect(self._on_plugin_started)
        self._pm.plugin_stopped.connect(self._on_plugin_stopped)
        self._pm.plugin_crashed.connect(self._on_plugin_crashed)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        self._container = QWidget()
        self._container.setObjectName("PluginsContainer")
        self._root = QVBoxLayout(self._container)
        self._root.setContentsMargins(32, 32, 32, 32)
        self._root.setSpacing(20)

        header_row = QHBoxLayout()
        title = QLabel("Plugin Manager")
        title.setObjectName("SectionTitle")
        header_row.addWidget(title)
        header_row.addStretch()
        self._root.addLayout(header_row)

        self._grid_widget = QWidget()
        self._grid = QGridLayout(self._grid_widget)
        self._grid.setSpacing(16)
        self._root.addWidget(self._grid_widget)
        self._root.addStretch()

        scroll.setWidget(self._container)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    # ──────────────────────────────────────────────────────────
    #  Public API
    # ──────────────────────────────────────────────────────────

    def refresh(self):
        """Rebuild cards from the current plugin manager state."""
        # Clear existing cards
        for i in reversed(range(self._grid.count())):
            w = self._grid.itemAt(i).widget()
            if w:
                w.setParent(None)
        self._cards.clear()

        manifests = self._pm.manifests()
        for idx, manifest in enumerate(manifests):
            card = PluginCard(manifest, self._pm)
            card.start_clicked.connect(self._on_start_clicked)
            card.stop_clicked.connect(self._on_stop_clicked)
            card.view_clicked.connect(self.navigate_to_plugin)
            card.set_active(self._pm.is_active(manifest.id))
            row, col = divmod(idx, 2)
            self._grid.addWidget(card, row, col)
            self._cards[manifest.id] = card

    def add_plugin_card(self, manifest):
        """Add a single card for a newly loaded plugin."""
        if manifest.id in self._cards:
            return
        idx = len(self._cards)
        card = PluginCard(manifest, self._pm)
        card.start_clicked.connect(self._on_start_clicked)
        card.stop_clicked.connect(self._on_stop_clicked)
        card.view_clicked.connect(self.navigate_to_plugin)
        row, col = divmod(idx, 2)
        self._grid.addWidget(card, row, col)
        self._cards[manifest.id] = card

    # ──────────────────────────────────────────────────────────
    #  Slots
    # ──────────────────────────────────────────────────────────

    def _on_start_clicked(self, plugin_id: str):
        if not self._pm.is_loaded(plugin_id):
            self._pm.load(plugin_id)
        self._pm.start(plugin_id)

    def _on_stop_clicked(self, plugin_id: str):
        self._pm.stop(plugin_id)

    def _on_plugin_started(self, plugin_id: str):
        if plugin_id in self._cards:
            self._cards[plugin_id].set_active(True)

    def _on_plugin_stopped(self, plugin_id: str):
        if plugin_id in self._cards:
            self._cards[plugin_id].set_active(False)

    def _on_plugin_crashed(self, plugin_id: str, msg: str):
        if plugin_id in self._cards:
            self._cards[plugin_id].set_crashed()
