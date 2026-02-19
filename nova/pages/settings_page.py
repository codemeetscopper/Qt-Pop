from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QColorDialog, QComboBox, QFileDialog, QFrame, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QPushButton, QScrollArea,
    QSizePolicy, QVBoxLayout, QWidget,
)

_log = logging.getLogger(__name__)


def _hex_from_qcolor(c: QColor) -> str:
    return "#{:02X}{:02X}{:02X}".format(c.red(), c.green(), c.blue())


class SettingRow(QWidget):
    """
    A single setting row with a label block and a fully-wired input widget.
    All changes are persisted immediately via ConfigurationManager.set_value().
    Color/theme changes also re-initialise StyleManager and re-apply QSS.
    """

    def __init__(self, key: str, item, qt_pop, parent: QWidget | None = None):
        super().__init__(parent)
        self._key = key          # config shortname
        self._item = item        # SettingItem dataclass
        self._qt_pop = qt_pop
        self.setObjectName("SettingRow")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(20)

        # ── Left: name + description ───────────────────────
        info = QVBoxLayout()
        info.setSpacing(2)

        name_lbl = QLabel(item.name)
        name_lbl.setObjectName("SettingName")
        desc_lbl = QLabel(item.description)
        desc_lbl.setObjectName("SettingDesc")
        desc_lbl.setWordWrap(True)

        info.addWidget(name_lbl)
        info.addWidget(desc_lbl)

        layout.addLayout(info, 1)

        # ── Right: input widget ────────────────────────────
        self._input = self._build_input(item)
        if self._input:
            self._input.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            layout.addWidget(self._input)

    # ──────────────────────────────────────────────────────
    #  Input builder
    # ──────────────────────────────────────────────────────

    def _build_input(self, item) -> Optional[QWidget]:
        t = getattr(item, "type", "") or ""
        val = getattr(item, "value", "") or ""
        vals = getattr(item, "values", []) or []

        if t == "colorpicker":
            btn = QPushButton()
            btn.setObjectName("ColorPickerButton")
            btn.setFixedSize(100, 28)
            self._update_color_button(btn, str(val))
            btn.clicked.connect(lambda: self._on_color_clicked(btn))
            return btn

        if t == "dropdown":
            combo = QComboBox()
            combo.setObjectName("SettingCombo")
            combo.setFixedWidth(160)
            for v in vals:
                combo.addItem(str(v))
            idx = combo.findText(str(val))
            if idx >= 0:
                combo.setCurrentIndex(idx)
            combo.currentTextChanged.connect(self._save)
            return combo

        if t == "filebrowse":
            return self._build_browse_row(str(val), folder=False)

        if t == "folderbrowse":
            return self._build_browse_row(str(val), folder=True)

        if t == "text":
            edit = QLineEdit(str(val))
            edit.setObjectName("SettingEdit")
            edit.setFixedWidth(200)
            edit.editingFinished.connect(lambda: self._save(edit.text()))
            return edit

        return None

    def _build_browse_row(self, current: str, folder: bool) -> QWidget:
        container = QWidget()
        container.setObjectName("BrowseContainer")
        h = QHBoxLayout(container)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(6)

        edit = QLineEdit(current)
        edit.setObjectName("SettingEdit")
        edit.setFixedWidth(200)
        edit.editingFinished.connect(lambda: self._save(edit.text()))

        btn = QPushButton("Browse…")
        btn.setObjectName("BrowseButton")
        btn.setFixedWidth(72)
        if folder:
            btn.clicked.connect(lambda: self._on_folder_browse(edit))
        else:
            btn.clicked.connect(lambda: self._on_file_browse(edit))

        h.addWidget(edit)
        h.addWidget(btn)
        return container

    # ──────────────────────────────────────────────────────
    #  Handlers
    # ──────────────────────────────────────────────────────

    def _on_color_clicked(self, btn: QPushButton):
        current_val = getattr(self._item, "value", "#000000") or "#000000"
        initial = QColor(str(current_val))
        if not initial.isValid():
            initial = QColor("#000000")
        chosen = QColorDialog.getColor(initial, self, f"Choose {self._item.name}")
        if chosen.isValid():
            hex_val = _hex_from_qcolor(chosen)
            self._item.value = hex_val
            self._update_color_button(btn, hex_val)
            self._save(hex_val)

    def _on_file_browse(self, edit: QLineEdit):
        path, _ = QFileDialog.getOpenFileName(
            self, f"Select file for {self._item.name}", edit.text()
        )
        if path:
            edit.setText(path)
            self._save(path)

    def _on_folder_browse(self, edit: QLineEdit):
        path = QFileDialog.getExistingDirectory(
            self, f"Select folder for {self._item.name}", edit.text()
        )
        if path:
            edit.setText(path)
            self._save(path)

    # ──────────────────────────────────────────────────────
    #  Save + style propagation
    # ──────────────────────────────────────────────────────

    def _save(self, value: Any):
        try:
            self._qt_pop.config.set_value(self._key, value)
        except Exception as exc:
            _log.warning("SettingRow: failed to save '%s': %s", self._key, exc)
            return

        # Re-apply styling for appearance-affecting keys
        if self._key in ("accent", "support", "neutral", "theme"):
            self._reapply_style()
        elif self._key == "qss_path":
            self._reload_qss(str(value))

    def _reapply_style(self):
        """Re-initialise StyleManager with current config and re-apply QSS."""
        try:
            cfg = self._qt_pop.config
            accent = cfg.get_value("accent")
            support = cfg.get_value("support")
            neutral = cfg.get_value("neutral")
            theme = cfg.get_value("theme")

            def _val(x):
                return x.value if hasattr(x, "value") else x

            self._qt_pop.style.initialise(
                _val(accent), _val(support), _val(neutral), _val(theme)
            )

            qss_path = cfg.get_value("qss_path")
            qss_str = _val(qss_path)
            p = Path(qss_str) if qss_str else None
            if p and not p.is_absolute():
                p = Path(cfg.json_path).parent.parent / p
            if p and p.exists():
                self._qt_pop.qss.set_style(p.read_text(encoding="utf-8"))
        except Exception as exc:
            _log.warning("SettingRow: failed to reapply style: %s", exc)

    def _reload_qss(self, path: str):
        try:
            p = Path(path)
            if not p.is_absolute():
                p = Path(self._qt_pop.config.json_path).parent.parent / p
            if p.exists():
                self._qt_pop.qss.set_style(p.read_text(encoding="utf-8"))
        except Exception as exc:
            _log.warning("SettingRow: failed to reload QSS: %s", exc)

    # ──────────────────────────────────────────────────────
    #  Helpers
    # ──────────────────────────────────────────────────────

    @staticmethod
    def _update_color_button(btn: QPushButton, hex_val: str):
        """Update button text and background to reflect chosen colour."""
        btn.setText(hex_val.upper())
        # Pick contrasting text colour so it's always readable
        c = QColor(hex_val)
        luminance = (0.299 * c.red() + 0.587 * c.green() + 0.114 * c.blue()) / 255
        text_color = "#000000" if luminance > 0.5 else "#FFFFFF"
        btn.setStyleSheet(
            f"background-color: {hex_val}; color: {text_color}; "
            f"border-radius: 6px; font-weight: 600;"
        )


class SettingsPage(QWidget):
    """Settings page — grouped rows for every user-configurable value."""

    def __init__(self, qt_pop, parent: QWidget | None = None):
        super().__init__(parent)
        self._qt_pop = qt_pop
        self.setObjectName("SettingsPage")

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        container = QWidget()
        container.setObjectName("SettingsContainer")
        self._root = QVBoxLayout(container)
        self._root.setContentsMargins(32, 32, 32, 32)
        self._root.setSpacing(20)

        title = QLabel("Settings")
        title.setObjectName("SectionTitle")
        self._root.addWidget(title)

        self._build_settings()
        self._root.addStretch()

        scroll.setWidget(container)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def _build_settings(self):
        try:
            user_items = list(self._qt_pop.config.data.configuration.user.items())
        except Exception as exc:
            _log.warning("SettingsPage: failed to read config: %s", exc)
            user_items = []

        # Group by the SettingItem.group field
        groups: Dict[str, List[Any]] = {}
        for key, item in user_items:
            group = getattr(item, "group", None) or "General"
            groups.setdefault(group, []).append((key, item))

        for group_name, items in groups.items():
            box = QGroupBox(group_name)
            box.setObjectName("SettingGroup")
            v = QVBoxLayout(box)
            v.setSpacing(0)
            v.setContentsMargins(0, 4, 0, 4)

            for idx, (key, item) in enumerate(items):
                row = SettingRow(key, item, self._qt_pop)
                if idx < len(items) - 1:
                    # Separator line between rows
                    sep = QFrame()
                    sep.setObjectName("SettingRowSep")
                    sep.setFrameShape(QFrame.HLine)
                v.addWidget(row)
                if idx < len(items) - 1:
                    v.addWidget(sep)

            self._root.addWidget(box)
