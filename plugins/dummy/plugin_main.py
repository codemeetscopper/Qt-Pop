"""
Dummy Plugin
============
A template plugin demonstrating settings and SVG icons.

Author  : Antigravity
Version : 1.0.0
"""
from __future__ import annotations

import time
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget
from nova.core.plugin_base import PluginBase, PluginSetting


class Plugin(PluginBase):
    """Main plugin class."""

    def __init__(self, bridge):
        super().__init__(bridge)
        self._label: QLabel | None = None
        self._layout: QVBoxLayout | None = None
        self._timer = QTimer()
        self._timer.timeout.connect(self._refresh_ui)

    # ── HOST: Settings ────────────────────────────────────────────────────────

    def get_settings(self) -> list[PluginSetting]:
        return [
            PluginSetting(
                key="show_greeting",
                name="Show Greeting",
                type="bool",
                default=True,
                description="Toggle the greeting message."
            ),
            PluginSetting(
                key="greeting_text",
                name="Greeting Text",
                type="text",
                default="Hello from Dummy Plugin!",
                description="The text to display."
            ),
            PluginSetting(
                key="bg_color",
                name="Background Color",
                type="colorpicker",
                default="#222222",
                description="Background color for the widget."
            )
        ]

    # ── HOST: UI ──────────────────────────────────────────────────────────────

    def create_widget(self, parent: QWidget | None = None) -> QWidget:
        frame = QFrame(parent)
        self._layout = QVBoxLayout(frame)
        self._layout.setAlignment(Qt.AlignCenter)

        self._label = QLabel()
        self._label.setAlignment(Qt.AlignCenter)
        self._layout.addWidget(self._label)
        
        # Initial UI update
        self._refresh_ui()
        
        # Poll for setting changes (since we don't have a change signal yet)
        self._timer.start(1000)
        
        # Ensure timer stops when widget is destroyed (handled by parenting usually, 
        # but since self._timer is on the Plugin instance which might outlive the widget 
        # if not careful, but Plugin instance usually lives as long as the page... 
        # actually Plugin instance lives in PluginManager._records. 
        # create_widget creates a view.
        # If the user navigates away, the widget is destroyed? 
        # Nova implementation creates the widget once and keeps it in QStackedWidget?
        # Yes, MainWindow keeps them in _pages. So it lives forever until plugin is unloaded.
        
        return frame

    def _refresh_ui(self):
        if not self._label:
            return

        # Read settings using our new get_setting helper
        show = self.get_setting("show_greeting")
        # Handle case where setting is not yet saved (use default)
        if show is None: show = True
        
        # Check explicit False vs None
        if isinstance(show, str): show = (show.lower() == "true")
        
        if show:
            text = self.get_setting("greeting_text") or "Hello!"
            self._label.setText(str(text))
            self._label.setVisible(True)
        else:
            self._label.setVisible(False)
            
        bg = self.get_setting("bg_color") or "#222222"
        # Apply background to the frame
        if self._label.parentWidget():
            self._label.parentWidget().setStyleSheet(f"background-color: {bg}; border-radius: 8px;")

    def on_data(self, key: str, value) -> None:
        pass

    # ── WORKER: Logic ─────────────────────────────────────────────────────────

    def start(self) -> None:
        super().start()
        # No background work needed for this demo
        while self.is_running:
            time.sleep(1)
