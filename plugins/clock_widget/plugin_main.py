"""
Clock Widget Plugin
===================
Worker side: sends HH:MM:SS every second.
Host side:   displays a large clock label.
"""
from __future__ import annotations

import time
from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget

# nova.core is importable because worker_host puts the project root on sys.path
from nova.core.plugin_base import PluginBase


class Plugin(PluginBase):

    def __init__(self, bridge):
        super().__init__(bridge)
        self._label: QLabel | None = None

    # ── HOST side ────────────────────────────────────────────
    def create_widget(self, parent: QWidget | None = None) -> QWidget:
        frame = QFrame(parent)
        frame.setObjectName("ClockFrame")
        v = QVBoxLayout(frame)
        v.setAlignment(Qt.AlignCenter)

        self._label = QLabel("--:--:--")
        self._label.setObjectName("ClockLabel")
        self._label.setAlignment(Qt.AlignCenter)
        self._label.setStyleSheet("font-size: 72px; font-weight: 200; letter-spacing: 4px;")
        v.addWidget(self._label)

        subtitle = QLabel("Live Clock via IPC")
        subtitle.setObjectName("ClockSubtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("font-size: 12px; opacity: 0.6;")
        v.addWidget(subtitle)

        return frame

    def on_data(self, key: str, value) -> None:
        if key == "time" and self._label is not None:
            self._label.setText(str(value))

    # ── WORKER side ──────────────────────────────────────────
    def start(self) -> None:
        super().start()
        while self.is_running:
            self.send_data("time", datetime.now().strftime("%H:%M:%S"))
            time.sleep(1)
