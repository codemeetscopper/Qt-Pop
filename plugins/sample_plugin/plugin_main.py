"""
Sample Plugin Plugin
====================
Sample plugin to do nothing

Author  : Aby
Version : 0.1.0

Nova Plugin API
===============
  create_widget(parent)  — HOST process: return a QWidget to show in the UI
  on_data(key, value)    — HOST process: called when worker sends data via IPC
  start()                — WORKER subprocess: run your logic here (blocking loop OK)
  stop()                 — WORKER subprocess: set self._running=False to exit loop
  send_data(key, value)  — WORKER subprocess: push data to the host UI
"""
from __future__ import annotations

import time

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget

from nova.core.plugin_base import PluginBase, PluginSetting


class Plugin(PluginBase):
    """Main plugin class — instantiated once per process context."""

    def __init__(self, bridge):
        super().__init__(bridge)
        self._label: QLabel | None = None

    # ── HOST: UI ──────────────────────────────────────────────────────────────

    def create_widget(self, parent: QWidget | None = None) -> QWidget:
        """Return the widget shown when the user opens this plugin's page."""
        frame = QFrame(parent)
        v = QVBoxLayout(frame)
        v.setAlignment(Qt.AlignCenter)

        self._label = QLabel("Waiting for data…")
        self._label.setAlignment(Qt.AlignCenter)
        v.addWidget(self._label)
        return frame

    def get_settings(self) -> list[PluginSetting]:
        return [
            PluginSetting(
                key="tick_interval",
                name="Tick Interval (s)",
                type="number",
                default=2,
                description="Seconds between each tick message sent to the UI.",
            ),
            PluginSetting(
                key="message_prefix",
                name="Message Prefix",
                type="text",
                default="Tick",
                description="Prefix text shown before the tick counter.",
            ),
        ]

    def on_data(self, key: str, value) -> None:
        """Called in the HOST whenever the worker sends a data packet."""
        if key == "message" and self._label is not None:
            try:
                self._label.setText(str(value))
            except RuntimeError:
                self._label = None

    # ── WORKER: Logic ─────────────────────────────────────────────────────────

    def start(self) -> None:
        """Main worker loop — runs in a separate subprocess."""
        super().start()
        counter = 0
        while self.is_running:
            self.send_data("message", f"Tick #{counter}")
            counter += 1
            time.sleep(2)
