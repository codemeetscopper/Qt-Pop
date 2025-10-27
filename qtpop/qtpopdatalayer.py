from __future__ import annotations
from typing import Any, Dict
from PySide6.QtCore import QObject, Signal, QMutex, QMutexLocker

from qtpop.qtpoplogger import debug_log


@debug_log
class QtPopDataLayer(QObject):
    """
    Singleton Data Layer for PySide6 applications.
    Provides global signals and centralized data storage
    for inter-UI communication, style updates, and configuration sharing.
    """

    # ---- Qt Signals ----
    dataChanged = Signal(str, object)         # key, new_value
    styleUpdated = Signal(str)                # theme_name or style_key
    configUpdated = Signal(dict)              # updated config dictionary
    messageBroadcast = Signal(str, object)    # generic messages between UIs

    _instance: QtPopDataLayer | None = None
    _mutex = QMutex()

    def __new__(cls) -> QtPopDataLayer:
        """Thread-safe singleton implementation."""
        with QMutexLocker(cls._mutex):
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # Avoid reinitializing the QObject base class
        if not hasattr(self, "_initialized"):
            super().__init__()
            self._data: Dict[str, Any] = {}
            self._initialized = True

    # ---- Public API ----

    @debug_log
    def set_data(self, key: str, value: Any):
        """Set shared data and emit change signal."""
        self._data[key] = value
        self.dataChanged.emit(key, value)

    @debug_log
    def get_data(self, key: str, default: Any = None) -> Any:
        """Retrieve data by key."""
        return self._data.get(key, default)

    @debug_log
    def broadcast_message(self, channel: str, payload: Any = None):
        """Broadcast a generic event to connected listeners."""
        self.messageBroadcast.emit(channel, payload)

    @debug_log
    def update_style(self, style_key: str):
        """Emit style update event."""
        self.styleUpdated.emit(style_key)

    @debug_log
    def update_config(self, new_config: Dict[str, Any]):
        """Emit config update signal."""
        self.configUpdated.emit(new_config)

    # ---- Utility ----
    @classmethod
    @debug_log
    def instance(cls) -> QtPopDataLayer:
        """Convenient access to the singleton instance."""
        return cls()

