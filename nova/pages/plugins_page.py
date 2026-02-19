from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog, QDialogButtonBox, QFileDialog, QFormLayout,
    QFrame, QGridLayout, QHBoxLayout, QLabel, QLineEdit,
    QMessageBox, QPushButton, QScrollArea, QSizePolicy,
    QVBoxLayout, QWidget,
)

_log = logging.getLogger(__name__)


def _icon_btn(icon_name: str, tooltip: str, size: int = 28,
              parent: QWidget | None = None) -> QPushButton:
    """Create a small icon-only QPushButton using IconManager, with emoji fallback."""
    btn = QPushButton(parent)
    btn.setToolTip(tooltip)
    btn.setFixedSize(size, size)
    btn.setObjectName("IconButton")
    try:
        from qtpop.appearance.iconmanager import IconManager
        from qtpop.appearance.stylemanager import StyleManager
        color = StyleManager.get_colour("fg1")
        px = IconManager.get_pixmap(icon_name, color, size - 8)
        if px and not px.isNull():
            btn.setIcon(px)
            btn.setIconSize(px.size())
            return btn
    except Exception:
        pass
    # Fallback text glyphs
    _FALLBACKS = {
        "action_favorite": "★", "action_favorite_border": "☆",
        "action_delete": "✕", "action_autorenew": "↺",
        "action_backup": "⤓", "action_info": "ℹ",
    }
    btn.setText(_FALLBACKS.get(icon_name, "?"))
    return btn


class _NewPluginDialog(QDialog):
    """Simple form dialog to gather details for scaffolding a new plugin."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("New Plugin")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.setSpacing(8)

        self._id = QLineEdit()
        self._id.setPlaceholderText("e.g. my_plugin")
        form.addRow("Plugin ID:", self._id)

        self._name = QLineEdit()
        self._name.setPlaceholderText("e.g. My Plugin")
        form.addRow("Name:", self._name)

        self._author = QLineEdit()
        self._author.setPlaceholderText("e.g. Your Name")
        form.addRow("Author:", self._author)

        self._desc = QLineEdit()
        self._desc.setPlaceholderText("One-line description")
        form.addRow("Description:", self._desc)

        layout.addLayout(form)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self._on_accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def _on_accept(self):
        pid = self._id.text().strip()
        import re
        if not re.match(r"^[a-z][a-z0-9_]{0,63}$", pid):
            QMessageBox.warning(
                self, "Invalid ID",
                "Plugin ID must be lowercase letters/digits/underscores and start with a letter."
            )
            return
        if not self._name.text().strip():
            QMessageBox.warning(self, "Missing Name", "Please enter a plugin name.")
            return
        self.accept()

    def values(self):
        return (
            self._id.text().strip(),
            self._name.text().strip(),
            self._author.text().strip() or "Unknown",
            self._desc.text().strip() or "A Nova plugin",
        )


class _InfoDialog(QDialog):
    """Shows detailed manifest and state information for a plugin."""

    def __init__(self, manifest, state, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle(f"Plugin Info — {manifest.name}")
        self.setMinimumWidth(420)

        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        def row(label: str, value: str):
            h = QHBoxLayout()
            lbl = QLabel(f"<b>{label}</b>")
            lbl.setFixedWidth(130)
            val = QLabel(str(value))
            val.setWordWrap(True)
            h.addWidget(lbl)
            h.addWidget(val, 1)
            layout.addLayout(h)

        row("ID", manifest.id)
        row("Name", manifest.name)
        row("Version", manifest.version)
        row("Author", manifest.author)
        row("Description", manifest.description)
        row("Entry", manifest.entry)
        row("Icon", manifest.icon)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        layout.addWidget(sep)

        row("Enabled", "Yes" if state.enabled else "No")
        row("Favorite", "Yes" if state.favorite else "No")
        row("Run count", str(state.run_count))
        row("Last run", state.last_run or "Never")
        row("Crash count", str(state.crash_count))
        row("Installed at", state.installed_at)

        btns = QDialogButtonBox(QDialogButtonBox.Close)
        btns.rejected.connect(self.reject)
        btns.accepted.connect(self.accept)
        layout.addWidget(btns)


class PluginCard(QFrame):
    """
    Card representing a single plugin.

    Buttons:
      Start | Stop | View  (primary actions)
      ★ Favorite | ↺ Reload | ⤓ Export | ✕ Delete | ℹ Info  (secondary)
    """

    start_clicked = Signal(str)
    stop_clicked = Signal(str)
    view_clicked = Signal(str)
    favorite_toggled = Signal(str, bool)    # plugin_id, new_value
    reload_clicked = Signal(str)
    export_clicked = Signal(str)
    delete_clicked = Signal(str)
    info_clicked = Signal(str)

    def __init__(self, manifest, plugin_manager, parent: QWidget | None = None):
        super().__init__(parent)
        self._manifest = manifest
        self._pm = plugin_manager
        self._is_favorite = plugin_manager.is_favorite(manifest.id)

        self.setObjectName("PluginCard")
        self.setFrameShape(QFrame.StyledPanel)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        v = QVBoxLayout(self)
        v.setContentsMargins(20, 16, 20, 16)
        v.setSpacing(8)

        # ── Header row ───────────────────────────────────────
        header_row = QHBoxLayout()
        header_row.setSpacing(8)

        self._status_dot = QLabel("●")
        self._status_dot.setObjectName("StatusDotInactive")
        self._status_dot.setFixedSize(14, 14)
        self._status_dot.setAlignment(Qt.AlignCenter)

        name_lbl = QLabel(manifest.name)
        name_lbl.setObjectName("PluginCardName")

        ver_lbl = QLabel(f"v{manifest.version}")
        ver_lbl.setObjectName("PluginCardVersion")

        self._fav_btn = _icon_btn(
            "action_favorite" if self._is_favorite else "action_favorite_border",
            "Remove from sidebar" if self._is_favorite else "Pin to sidebar",
        )
        self._fav_btn.setObjectName("FavoriteButton")
        self._fav_btn.clicked.connect(self._on_favorite_clicked)
        self._update_fav_icon()

        header_row.addWidget(self._status_dot)
        header_row.addWidget(name_lbl, 1)
        header_row.addWidget(ver_lbl)
        header_row.addWidget(self._fav_btn)
        v.addLayout(header_row)

        # ── Description ──────────────────────────────────────
        desc = QLabel(manifest.description or "No description provided.")
        desc.setObjectName("PluginCardDesc")
        desc.setWordWrap(True)
        v.addWidget(desc)

        if manifest.author:
            author = QLabel(f"by {manifest.author}")
            author.setObjectName("PluginCardAuthor")
            v.addWidget(author)

        # ── Primary action buttons ────────────────────────────
        primary_row = QHBoxLayout()
        primary_row.setSpacing(8)

        self._start_btn = QPushButton("Start")
        self._start_btn.setObjectName("PluginStartButton")
        self._start_btn.setFixedWidth(72)
        self._start_btn.clicked.connect(lambda: self.start_clicked.emit(manifest.id))

        self._stop_btn = QPushButton("Stop")
        self._stop_btn.setObjectName("PluginStopButton")
        self._stop_btn.setFixedWidth(72)
        self._stop_btn.setEnabled(False)
        self._stop_btn.clicked.connect(lambda: self.stop_clicked.emit(manifest.id))

        self._view_btn = QPushButton("View")
        self._view_btn.setObjectName("PluginViewButton")
        self._view_btn.setFixedWidth(72)
        self._view_btn.setEnabled(False)
        self._view_btn.clicked.connect(lambda: self.view_clicked.emit(manifest.id))

        primary_row.addWidget(self._start_btn)
        primary_row.addWidget(self._stop_btn)
        primary_row.addWidget(self._view_btn)
        primary_row.addStretch()
        v.addLayout(primary_row)

        # ── Secondary icon buttons ────────────────────────────
        secondary_row = QHBoxLayout()
        secondary_row.setSpacing(4)

        self._reload_btn = _icon_btn("action_autorenew", "Reload plugin")
        self._reload_btn.clicked.connect(lambda: self.reload_clicked.emit(manifest.id))

        self._export_btn = _icon_btn("action_backup", "Export as .zip")
        self._export_btn.clicked.connect(lambda: self.export_clicked.emit(manifest.id))

        self._delete_btn = _icon_btn("action_delete", "Delete plugin")
        self._delete_btn.setObjectName("DeleteButton")
        self._delete_btn.clicked.connect(lambda: self.delete_clicked.emit(manifest.id))

        self._info_btn = _icon_btn("action_info", "Plugin info")
        self._info_btn.clicked.connect(lambda: self.info_clicked.emit(manifest.id))

        secondary_row.addStretch()
        secondary_row.addWidget(self._reload_btn)
        secondary_row.addWidget(self._export_btn)
        secondary_row.addWidget(self._delete_btn)
        secondary_row.addWidget(self._info_btn)
        v.addLayout(secondary_row)

    # ──────────────────────────────────────────────────────
    #  Public API
    # ──────────────────────────────────────────────────────

    def set_active(self, active: bool):
        self._start_btn.setEnabled(not active)
        self._stop_btn.setEnabled(active)
        self._view_btn.setEnabled(active)
        dot_name = "StatusDotActive" if active else "StatusDotInactive"
        self._set_dot(dot_name)

    def set_crashed(self):
        self._set_dot("StatusDotCrashed")
        self._start_btn.setEnabled(True)
        self._stop_btn.setEnabled(False)
        self._view_btn.setEnabled(False)

    def set_favorite(self, value: bool):
        self._is_favorite = value
        self._update_fav_icon()

    # ──────────────────────────────────────────────────────
    #  Internal
    # ──────────────────────────────────────────────────────

    def _set_dot(self, object_name: str):
        self._status_dot.setObjectName(object_name)
        self._status_dot.style().unpolish(self._status_dot)
        self._status_dot.style().polish(self._status_dot)
        self._status_dot.update()

    def _on_favorite_clicked(self):
        new_val = not self._is_favorite
        self.favorite_toggled.emit(self._manifest.id, new_val)

    def _update_fav_icon(self):
        icon = "action_favorite" if self._is_favorite else "action_favorite_border"
        tip = "Remove from sidebar" if self._is_favorite else "Pin to sidebar"
        self._fav_btn.setToolTip(tip)
        try:
            from qtpop.appearance.iconmanager import IconManager
            from qtpop.appearance.stylemanager import StyleManager
            color = StyleManager.get_colour("accent") if self._is_favorite else StyleManager.get_colour("fg1")
            px = IconManager.get_pixmap(icon, color, 20)
            if px and not px.isNull():
                self._fav_btn.setIcon(px)
                self._fav_btn.setIconSize(px.size())
                self._fav_btn.setText("")
                return
        except Exception:
            pass
        self._fav_btn.setText("★" if self._is_favorite else "☆")


class PluginsPage(QWidget):
    """
    Plugin manager page.

    Features:
    - Grid of PluginCards
    - Import .zip button
    - Create new plugin template button
    - Per-card: Start/Stop/View, Favorite toggle, Reload, Export, Delete, Info
    """

    navigate_to_plugin = Signal(str)

    def __init__(self, plugin_manager, parent: QWidget | None = None):
        super().__init__(parent)
        self._pm = plugin_manager
        self._cards: Dict[str, PluginCard] = {}
        self.setObjectName("PluginsPage")

        self._pm.plugin_started.connect(self._on_plugin_started)
        self._pm.plugin_stopped.connect(self._on_plugin_stopped)
        self._pm.plugin_crashed.connect(self._on_plugin_crashed)
        self._pm.plugin_favorite_changed.connect(self._on_favorite_changed)
        self._pm.plugin_deleted.connect(self._on_plugin_deleted)
        self._pm.plugin_imported.connect(self._on_plugin_imported)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        self._container = QWidget()
        self._container.setObjectName("PluginsContainer")
        self._root = QVBoxLayout(self._container)
        self._root.setContentsMargins(32, 32, 32, 32)
        self._root.setSpacing(20)

        # ── Toolbar ──────────────────────────────────────────
        toolbar = QHBoxLayout()
        toolbar.setSpacing(12)

        title = QLabel("Plugin Manager")
        title.setObjectName("SectionTitle")
        toolbar.addWidget(title)
        toolbar.addStretch()

        self._import_btn = QPushButton("Import .zip")
        self._import_btn.setObjectName("ToolbarButton")
        self._import_btn.setToolTip("Import a plugin from a .zip archive")
        self._import_btn.clicked.connect(self._on_import_clicked)
        toolbar.addWidget(self._import_btn)

        self._new_btn = QPushButton("New Plugin")
        self._new_btn.setObjectName("ToolbarButton")
        self._new_btn.setToolTip("Scaffold a new plugin template in the plugins directory")
        self._new_btn.clicked.connect(self._on_new_plugin_clicked)
        toolbar.addWidget(self._new_btn)

        self._root.addLayout(toolbar)

        # ── Grid ─────────────────────────────────────────────
        self._grid_widget = QWidget()
        self._grid = QGridLayout(self._grid_widget)
        self._grid.setSpacing(16)
        self._root.addWidget(self._grid_widget)
        self._root.addStretch()

        scroll.setWidget(self._container)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    # ──────────────────────────────────────────────────────
    #  Public API
    # ──────────────────────────────────────────────────────

    def refresh(self):
        """Rebuild all cards from current plugin manager state."""
        while self._grid.count():
            item = self._grid.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
                w.deleteLater()
        self._cards.clear()

        for idx, manifest in enumerate(self._pm.manifests()):
            self._add_card(manifest, idx)

    def add_plugin_card(self, manifest):
        """Append a card for a newly loaded plugin."""
        if manifest.id not in self._cards:
            self._add_card(manifest, len(self._cards))

    # ──────────────────────────────────────────────────────
    #  Internal — card lifecycle
    # ──────────────────────────────────────────────────────

    def _add_card(self, manifest, idx: int):
        card = PluginCard(manifest, self._pm)
        card.start_clicked.connect(self._on_start_clicked)
        card.stop_clicked.connect(self._on_stop_clicked)
        card.view_clicked.connect(self.navigate_to_plugin)
        card.favorite_toggled.connect(self._pm.set_favorite)
        card.reload_clicked.connect(self._on_reload_clicked)
        card.export_clicked.connect(self._on_export_clicked)
        card.delete_clicked.connect(self._on_delete_clicked)
        card.info_clicked.connect(self._on_info_clicked)
        card.set_active(self._pm.is_active(manifest.id))
        row, col = divmod(idx, 2)
        self._grid.addWidget(card, row, col)
        self._cards[manifest.id] = card

    # ──────────────────────────────────────────────────────
    #  Internal — plugin actions
    # ──────────────────────────────────────────────────────

    def _on_start_clicked(self, plugin_id: str):
        if not self._pm.is_loaded(plugin_id):
            self._pm.load(plugin_id)
        self._pm.start(plugin_id)

    def _on_stop_clicked(self, plugin_id: str):
        self._pm.stop(plugin_id)

    def _on_reload_clicked(self, plugin_id: str):
        self._pm.reload_plugin(plugin_id)
        # Card state will update via plugin_started/stopped signals

    def _on_export_clicked(self, plugin_id: str):
        output_dir = QFileDialog.getExistingDirectory(
            self, "Select Export Folder", str(Path.home())
        )
        if not output_dir:
            return
        ok, result = self._pm.export_plugin(plugin_id, Path(output_dir))
        if ok:
            QMessageBox.information(self, "Export Successful",
                                    f"Plugin exported to:\n{result}")
        else:
            QMessageBox.warning(self, "Export Failed", result)

    def _on_delete_clicked(self, plugin_id: str):
        reply = QMessageBox.question(
            self, "Delete Plugin",
            f"Permanently delete plugin '{plugin_id}' and all its files?\n"
            "This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            ok, err = self._pm.delete_plugin(plugin_id)
            if not ok:
                QMessageBox.warning(self, "Delete Failed", err)

    def _on_info_clicked(self, plugin_id: str):
        record = self._pm._records.get(plugin_id)
        if record is None:
            return
        state = self._pm.get_state(plugin_id)
        dlg = _InfoDialog(record.manifest, state, self)
        dlg.exec()

    def _on_import_clicked(self):
        zip_path, _ = QFileDialog.getOpenFileName(
            self, "Import Plugin", str(Path.home()),
            "Plugin Archives (*.zip)"
        )
        if not zip_path:
            return
        ok, result = self._pm.import_plugin(Path(zip_path))
        if ok:
            QMessageBox.information(
                self, "Import Successful",
                f"Plugin '{result}' imported successfully.\n"
                "Load and start it from the Plugin Manager."
            )
        else:
            QMessageBox.warning(self, "Import Failed", result)

    def _on_new_plugin_clicked(self):
        dlg = _NewPluginDialog(self)
        if dlg.exec() != QDialog.Accepted:
            return

        plugin_id, name, author, desc = dlg.values()
        plugins_dir = self._pm._plugins_dir
        target = plugins_dir / plugin_id
        if target.exists():
            QMessageBox.warning(
                self, "Already Exists",
                f"A plugin directory named '{plugin_id}' already exists."
            )
            return

        from nova.core.plugin_spec import create_plugin_template
        try:
            created = create_plugin_template(plugin_id, name, author, desc, plugins_dir)
            
            # Treat creation as an import so the app loads it and creates the page
            self._pm.plugin_imported.emit(plugin_id)
            
            QMessageBox.information(
                self, "Plugin Created",
                f"Plugin template created at:\n{created}\n\n"
                "Edit plugin_main.py to implement your plugin logic,\n"
                "then use Load/Start to run it."
            )
        except Exception as exc:
            QMessageBox.warning(self, "Creation Failed", str(exc))

    # ──────────────────────────────────────────────────────
    #  Internal — signal handlers
    # ──────────────────────────────────────────────────────

    def _on_plugin_started(self, plugin_id: str):
        if plugin_id in self._cards:
            self._cards[plugin_id].set_active(True)

    def _on_plugin_stopped(self, plugin_id: str):
        if plugin_id in self._cards:
            self._cards[plugin_id].set_active(False)

    def _on_plugin_crashed(self, plugin_id: str, _msg: str):
        if plugin_id in self._cards:
            self._cards[plugin_id].set_crashed()

    def _on_favorite_changed(self, plugin_id: str, is_fav: bool):
        if plugin_id in self._cards:
            self._cards[plugin_id].set_favorite(is_fav)

    def _on_plugin_deleted(self, plugin_id: str):
        """Card removed — refresh the whole grid to re-index."""
        self.refresh()

    def _on_plugin_imported(self, plugin_id: str):
        """Load the newly imported plugin and add its card."""
        if self._pm.load(plugin_id):
            self.refresh()
