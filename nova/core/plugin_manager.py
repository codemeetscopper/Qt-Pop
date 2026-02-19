from __future__ import annotations

import importlib.util
import logging
import sys
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from PySide6.QtCore import QObject, Signal, QProcess, QTimer
from PySide6.QtWidgets import QWidget

from nova.core.plugin_base import PluginBase, PluginManifest
from nova.core.plugin_bridge import MainBridge

_log = logging.getLogger(__name__)

_MAX_RESTARTS = 3


@dataclass
class _PluginRecord:
    manifest: PluginManifest
    plugin: Optional[PluginBase] = None
    bridge: Optional[MainBridge] = None
    process: Optional[QProcess] = None
    socket_name: str = ""
    restart_count: int = 0
    active: bool = False


class PluginManager(QObject):
    """
    Manages plugin discovery, lifecycle, and IPC for Nova plugins.

    Each plugin runs in a subprocess (QProcess) communicating via QLocalSocket.
    """

    plugin_loaded = Signal(str)          # plugin_id
    plugin_started = Signal(str)         # plugin_id
    plugin_stopped = Signal(str)         # plugin_id
    plugin_crashed = Signal(str, str)    # plugin_id, error_message

    def __init__(self, data_layer: Any, plugins_dir: Path, parent: QObject | None = None):
        super().__init__(parent)
        self._data = data_layer
        self._plugins_dir = plugins_dir
        self._records: Dict[str, _PluginRecord] = {}
        # project root is two levels up from nova/core/
        self._project_root = Path(__file__).parent.parent.parent

    # ──────────────────────────────────────────────────────────
    #  Discovery
    # ──────────────────────────────────────────────────────────

    def discover(self) -> List[PluginManifest]:
        """Scan plugins_dir for plugin.json files and return manifests."""
        manifests: List[PluginManifest] = []
        if not self._plugins_dir.exists():
            _log.warning("PluginManager: plugins directory not found: %s", self._plugins_dir)
            return manifests
        for json_file in sorted(self._plugins_dir.rglob("plugin.json")):
            try:
                m = PluginManifest.from_file(json_file)
                manifests.append(m)
                _log.debug("PluginManager: discovered plugin '%s'", m.id)
            except Exception as exc:
                _log.warning("PluginManager: failed to load manifest %s: %s", json_file, exc)
        return manifests

    # ──────────────────────────────────────────────────────────
    #  Loading (imports the plugin class, creates MainBridge)
    # ──────────────────────────────────────────────────────────

    def load(self, plugin_id: str) -> bool:
        """
        Import the plugin class and create a PluginRecord.
        Does NOT start the subprocess yet.
        """
        if plugin_id in self._records:
            _log.debug("PluginManager: plugin '%s' already loaded", plugin_id)
            return True

        # Find manifest
        manifest: Optional[PluginManifest] = None
        for m in self.discover():
            if m.id == plugin_id:
                manifest = m
                break
        if manifest is None:
            _log.error("PluginManager: manifest not found for '%s'", plugin_id)
            return False

        # Dynamically import the plugin class
        plugin_dir = self._plugins_dir / plugin_id
        module_name, class_name = manifest.entry.rsplit(".", 1)
        module_file = plugin_dir / f"{module_name}.py"
        if not module_file.exists():
            _log.error("PluginManager: entry file not found: %s", module_file)
            return False

        try:
            spec = importlib.util.spec_from_file_location(
                f"nova_plugin_{plugin_id}.{module_name}", module_file
            )
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            plugin_class = getattr(mod, class_name)
        except Exception as exc:
            _log.error("PluginManager: failed to import plugin '%s': %s", plugin_id, exc)
            return False

        record = _PluginRecord(manifest=manifest)
        record.socket_name = f"nova_{plugin_id}_{uuid.uuid4().hex[:8]}"
        self._records[plugin_id] = record

        # Create bridge (host side) — it starts listening immediately
        bridge = MainBridge(record.socket_name, self)

        # Instantiate plugin with bridge (host side: no process yet)
        try:
            plugin_inst = plugin_class(bridge)
            plugin_inst.manifest = manifest
        except Exception as exc:
            _log.error("PluginManager: failed to instantiate plugin '%s': %s", plugin_id, exc)
            bridge.close()
            bridge.deleteLater()
            del self._records[plugin_id]
            return False

        bridge.data_received.connect(
            lambda key, value, pid=plugin_id: self._on_data_received(pid, key, value)
        )
        bridge.worker_ready.connect(
            lambda pid=plugin_id: self._on_worker_ready(pid)
        )
        bridge.worker_gone.connect(
            lambda pid=plugin_id: self._on_worker_gone(pid)
        )

        record.plugin = plugin_inst
        record.bridge = bridge
        self.plugin_loaded.emit(plugin_id)
        _log.info("PluginManager: loaded plugin '%s'", plugin_id)
        return True

    # ──────────────────────────────────────────────────────────
    #  Starting / Stopping
    # ──────────────────────────────────────────────────────────

    def start(self, plugin_id: str) -> bool:
        """Spawn the worker subprocess for the given plugin."""
        record = self._records.get(plugin_id)
        if record is None:
            _log.error("PluginManager: cannot start unloaded plugin '%s'", plugin_id)
            return False
        if record.active:
            _log.debug("PluginManager: plugin '%s' already running", plugin_id)
            return True

        process = QProcess(self)
        process.setWorkingDirectory(str(self._project_root))
        process.setProcessChannelMode(QProcess.MergedChannels)
        process.readyReadStandardOutput.connect(
            lambda pid=plugin_id, p=process: self._log_process_output(pid, p)
        )
        process.finished.connect(
            lambda code, status, pid=plugin_id: self._on_process_finished(pid, code, status)
        )

        args = [
            "-m", "nova.core.worker_host",
            plugin_id,
            str(self._plugins_dir),
            record.socket_name,
        ]
        process.start(sys.executable, args)
        if not process.waitForStarted(3000):
            _log.error("PluginManager: failed to start process for '%s'", plugin_id)
            process.deleteLater()
            return False

        record.process = process
        record.active = True
        self.plugin_started.emit(plugin_id)
        _log.info("PluginManager: started plugin '%s' (PID %s)", plugin_id, process.processId())
        return True

    def stop(self, plugin_id: str):
        """Send stop command and terminate the worker subprocess."""
        record = self._records.get(plugin_id)
        if record is None or not record.active:
            return
        if record.bridge:
            record.bridge.send_command("stop")
        if record.process:
            record.process.terminate()
            if not record.process.waitForFinished(2000):
                record.process.kill()
        record.active = False
        self.plugin_stopped.emit(plugin_id)

    def stop_all(self):
        for plugin_id in list(self._records.keys()):
            self.stop(plugin_id)

    # ──────────────────────────────────────────────────────────
    #  Widget creation
    # ──────────────────────────────────────────────────────────

    def create_widget(self, plugin_id: str, parent: QWidget | None = None) -> Optional[QWidget]:
        record = self._records.get(plugin_id)
        if record and record.plugin:
            try:
                return record.plugin.create_widget(parent)
            except Exception as exc:
                _log.error("PluginManager: create_widget failed for '%s': %s", plugin_id, exc)
        return None

    # ──────────────────────────────────────────────────────────
    #  Queries
    # ──────────────────────────────────────────────────────────

    def is_active(self, plugin_id: str) -> bool:
        rec = self._records.get(plugin_id)
        return rec is not None and rec.active

    def is_loaded(self, plugin_id: str) -> bool:
        return plugin_id in self._records

    def manifests(self) -> List[PluginManifest]:
        return [r.manifest for r in self._records.values()]

    def loaded_count(self) -> int:
        return len(self._records)

    def active_count(self) -> int:
        return sum(1 for r in self._records.values() if r.active)

    # ──────────────────────────────────────────────────────────
    #  Internal callbacks
    # ──────────────────────────────────────────────────────────

    def _on_data_received(self, plugin_id: str, key: str, value: Any):
        record = self._records.get(plugin_id)
        if record and record.plugin:
            try:
                record.plugin.on_data(key, value)
            except Exception as exc:
                _log.warning("PluginManager: on_data error for '%s': %s", plugin_id, exc)

    def _on_worker_ready(self, plugin_id: str):
        _log.debug("PluginManager: worker ready for '%s'", plugin_id)

    def _on_worker_gone(self, plugin_id: str):
        record = self._records.get(plugin_id)
        if record and record.active:
            _log.warning("PluginManager: worker gone unexpectedly for '%s'", plugin_id)

    def _on_process_finished(self, plugin_id: str, exit_code: int, exit_status: QProcess.ExitStatus):
        record = self._records.get(plugin_id)
        if record is None:
            return

        was_active = record.active
        record.active = False

        if exit_status == QProcess.CrashExit or (exit_code != 0 and was_active):
            record.restart_count += 1
            msg = f"Plugin '{plugin_id}' crashed (exit {exit_code}, attempt {record.restart_count})"
            _log.error("PluginManager: %s", msg)
            self.plugin_crashed.emit(plugin_id, msg)

            if record.restart_count <= _MAX_RESTARTS:
                _log.info("PluginManager: restarting '%s' in 2s", plugin_id)
                QTimer.singleShot(2000, lambda: self.start(plugin_id))
            else:
                _log.error("PluginManager: plugin '%s' exceeded max restarts", plugin_id)
        else:
            self.plugin_stopped.emit(plugin_id)

    def _log_process_output(self, plugin_id: str, process: QProcess):
        data = bytes(process.readAllStandardOutput()).decode("utf-8", errors="replace")
        for line in data.splitlines():
            if line.strip():
                _log.debug("[plugin:%s] %s", plugin_id, line)
