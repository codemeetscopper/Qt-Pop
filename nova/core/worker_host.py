"""
Nova plugin worker host.

Entry point for plugin subprocesses:
    python -m nova.core.worker_host <plugin_id> <plugins_dir> <socket_name>

Bootstraps a QCoreApplication, dynamically imports the plugin class,
connects to the host's QLocalServer, runs plugin.start() in a QThread,
and then enters the Qt event loop.
"""

from __future__ import annotations

import importlib.util
import json
import logging
import sys
from pathlib import Path

# ── bootstrap logging for subprocess ──────────────────────────
logging.basicConfig(
    level=logging.DEBUG,
    format="[worker] %(levelname)s %(name)s: %(message)s",
)
_log = logging.getLogger(__name__)


def main():
    if len(sys.argv) < 4:
        _log.error("Usage: worker_host <plugin_id> <plugins_dir> <socket_name>")
        sys.exit(1)

    plugin_id = sys.argv[1]
    plugins_dir = Path(sys.argv[2])
    socket_name = sys.argv[3]

    # Must import Qt *after* argument parsing (avoids Qt trying to use argv)
    from PySide6.QtCore import QCoreApplication, QThread, QTimer

    app = QCoreApplication(sys.argv[:1])

    # ── load manifest ──────────────────────────────────────────
    plugin_dir = plugins_dir / plugin_id
    manifest_file = plugin_dir / "plugin.json"
    if not manifest_file.exists():
        _log.error("Manifest not found: %s", manifest_file)
        sys.exit(2)

    # Import plugin_base (may need project root on sys.path)
    project_root = Path(__file__).parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    from nova.core.plugin_base import PluginManifest
    from nova.core.plugin_bridge import WorkerBridge

    try:
        manifest = PluginManifest.from_file(manifest_file)
    except Exception as exc:
        _log.error("Failed to load manifest: %s", exc)
        sys.exit(3)

    # ── import plugin class ────────────────────────────────────
    module_name, class_name = manifest.entry.rsplit(".", 1)
    module_file = plugin_dir / f"{module_name}.py"
    if not module_file.exists():
        _log.error("Entry file not found: %s", module_file)
        sys.exit(4)

    try:
        spec = importlib.util.spec_from_file_location(
            f"nova_worker_{plugin_id}.{module_name}", module_file
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        plugin_class = getattr(mod, class_name)
    except Exception as exc:
        _log.error("Failed to import plugin class: %s", exc)
        sys.exit(5)

    # ── create bridge and plugin ───────────────────────────────
    bridge = WorkerBridge(socket_name)
    plugin = plugin_class(bridge)
    plugin.manifest = manifest
    bridge.set_plugin(plugin)

    # ── run plugin.start() in a QThread ───────────────────────
    class _PluginThread(QThread):
        def run(self):
            try:
                plugin.start()
            except Exception as exc:
                _log.error("plugin.start() raised: %s", exc)

    thread = _PluginThread()

    # Give the bridge 200 ms to connect before kicking off the plugin
    def _deferred_start():
        thread.start()

    QTimer.singleShot(200, _deferred_start)

    # ── Qt event loop ──────────────────────────────────────────
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
