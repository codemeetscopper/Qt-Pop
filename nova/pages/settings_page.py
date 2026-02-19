from __future__ import annotations

from typing import Any, Dict, List

from PySide6.QtWidgets import (
    QComboBox, QFileDialog, QFrame, QGroupBox, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QScrollArea, QSizePolicy,
    QVBoxLayout, QWidget,
)
from PySide6.QtCore import Qt


class SettingRow(QWidget):
    """A single setting row with label and appropriate input widget."""

    def __init__(self, item, qt_pop, parent: QWidget | None = None):
        super().__init__(parent)
        self._item = item
        self._qt_pop = qt_pop
        self.setObjectName("SettingRow")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(16)

        info = QVBoxLayout()
        info.setSpacing(2)
        name_lbl = QLabel(item.name)
        name_lbl.setObjectName("SettingName")
        desc_lbl = QLabel(item.description)
        desc_lbl.setObjectName("SettingDesc")
        info.addWidget(name_lbl)
        info.addWidget(desc_lbl)
        layout.addLayout(info, 1)

        self._input = self._build_input(item)
        if self._input:
            layout.addWidget(self._input)

    def _build_input(self, item) -> QWidget | None:
        t = getattr(item, "type", None) or ""
        val = getattr(item, "value", "") or ""
        vals = getattr(item, "values", []) or []

        if t == "colorpicker":
            btn = QPushButton()
            btn.setObjectName("ColorPickerButton")
            btn.setFixedWidth(80)
            btn.setText(str(val))
            btn.setStyleSheet(f"background-color: {val};")
            return btn

        if t == "dropdown":
            combo = QComboBox()
            combo.setObjectName("SettingCombo")
            combo.setMinimumWidth(140)
            for v in vals:
                combo.addItem(str(v))
            idx = combo.findText(str(val))
            if idx >= 0:
                combo.setCurrentIndex(idx)
            return combo

        if t in ("filebrowse", "folderbrowse"):
            row = QWidget()
            hl = QHBoxLayout(row)
            hl.setContentsMargins(0, 0, 0, 0)
            hl.setSpacing(4)
            edit = QLineEdit(str(val))
            edit.setObjectName("SettingEdit")
            edit.setMinimumWidth(180)
            btn = QPushButton("Browse")
            btn.setObjectName("BrowseButton")
            btn.setFixedWidth(60)
            hl.addWidget(edit)
            hl.addWidget(btn)
            return row

        if t == "text":
            edit = QLineEdit(str(val))
            edit.setObjectName("SettingEdit")
            edit.setMinimumWidth(200)
            return edit

        return None


class SettingsPage(QWidget):
    """Settings page with grouped setting rows built from ConfigurationManager."""

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
            # Only user settings have SettingItem objects with .name/.group attributes.
            # Static settings are plain values and are not user-configurable.
            user_items = self._qt_pop.config.data.configuration.user.items()
        except Exception:
            user_items = []

        groups: Dict[str, List[Any]] = {}
        for _key, item in user_items:
            group = getattr(item, "group", None) or "General"
            groups.setdefault(group, []).append(item)

        for group_name, items in groups.items():
            box = QGroupBox(group_name)
            box.setObjectName("SettingGroup")
            v = QVBoxLayout(box)
            v.setSpacing(0)
            v.setContentsMargins(0, 8, 0, 8)
            for item in items:
                row = SettingRow(item, self._qt_pop)
                v.addWidget(row)
            self._root.addWidget(box)
