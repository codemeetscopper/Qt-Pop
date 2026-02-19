from __future__ import annotations

import logging
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from nova.core.plugin_manager import PluginManager
from nova.pages.about_page import AboutPage
from nova.pages.home_page import HomePage
from nova.pages.plugins_page import PluginsPage
from nova.pages.settings_page import SettingsPage
from nova.ui.main_window import MainWindow

_log = logging.getLogger(__name__)


def run(qt_pop) -> None:
    app = QApplication.instance() or QApplication(sys.argv)

    # Apply nova.qss (warn if missing but continue)
    nova_qss = Path(__file__).parent.parent / "resources" / "qss" / "nova.qss"
    if nova_qss.exists():
        qt_pop.qss.set_style(nova_qss.read_text(encoding="utf-8"))
    else:
        _log.warning("nova.qss not found at %s — running unstyled", nova_qss)

    # Plugin manager — no QObject parent here; we keep it alive via window._pm
    # and via the 'pm' local variable that lives for the full duration of app.exec().
    plugins_dir = Path(__file__).parent.parent / "plugins"
    pm = PluginManager(qt_pop.data, plugins_dir)

    # Pages
    home = HomePage(qt_pop)
    plugins_pg = PluginsPage(pm)
    settings = SettingsPage(qt_pop)
    about = AboutPage(qt_pop)

    # Main window
    window = MainWindow(qt_pop, pm)

    # ── Page ordering ────────────────────────────────────────
    # home → plugins → [plugin pages inserted here] → separator → settings → about
    window.add_page("home",    "Home",    "action_home",      home)
    window.add_page("plugins", "Plugins", "action_extension", plugins_pg)
    # Separator is inserted BEFORE settings/about so plugin pages go above it
    window.add_separator()
    window.add_page("settings", "Settings", "action_settings", settings)
    window.add_page("about",    "About",    "action_info",     about)

    # ── Discover → load → start all plugins ──────────────────
    for manifest in pm.discover():
        if pm.load(manifest.id):
            widget = pm.create_widget(manifest.id)
            if widget is not None:
                in_sidebar = pm.is_favorite(manifest.id)
                window.add_plugin_page(
                    f"plugin_{manifest.id}",
                    manifest.name,
                    manifest.icon or "action_extension",
                    widget,
                    in_sidebar=in_sidebar,
                )
            pm.start(manifest.id)

    plugins_pg.refresh()

    # ── Home page stat updates ────────────────────────────────
    def _update_home(*_args):
        home.update_stats(pm.loaded_count(), pm.active_count())

    pm.plugin_loaded.connect(_update_home)
    pm.plugin_started.connect(_update_home)
    pm.plugin_stopped.connect(_update_home)
    pm.plugin_crashed.connect(_update_home)
    pm.plugin_deleted.connect(_update_home)
    pm.plugin_imported.connect(_update_home)
    _update_home()

    # ── Navigate to plugin page from Plugins page "View" button ──
    def _on_navigate_to_plugin(plugin_id: str):
        page_id = f"plugin_{plugin_id}"
        if page_id in window._pages:
            window.navigate(page_id)

    plugins_pg.navigate_to_plugin.connect(_on_navigate_to_plugin)

    # ── Favorite toggled: show/hide plugin in sidebar ─────────
    def _on_favorite_changed(plugin_id: str, is_fav: bool):
        page_id = f"plugin_{plugin_id}"
        if page_id not in window._pages:
            return
        record = pm._records.get(plugin_id)
        if record is None:
            return
        title = record.manifest.name
        icon = record.manifest.icon or "action_extension"
        if is_fav:
            window.show_plugin_in_sidebar(page_id, title, icon)
        else:
            window.hide_plugin_from_sidebar(page_id)

    pm.plugin_favorite_changed.connect(_on_favorite_changed)

    # ── Plugin imported: load, create page, refresh cards ─────
    def _on_plugin_imported(plugin_id: str):
        if pm.load(plugin_id):
            widget = pm.create_widget(plugin_id)
            if widget is not None:
                record = pm._records.get(plugin_id)
                title = record.manifest.name if record else plugin_id
                icon = record.manifest.icon if record else "action_extension"
                in_sidebar = pm.is_favorite(plugin_id)
                window.add_plugin_page(
                    f"plugin_{plugin_id}", title, icon, widget, in_sidebar
                )
        plugins_pg.refresh()
        _update_home()

    pm.plugin_imported.connect(_on_plugin_imported)

    # ── Plugin deleted: remove page + sidebar item ─────────────
    def _on_plugin_deleted(plugin_id: str):
        window.remove_plugin_page(f"plugin_{plugin_id}")
        _update_home()
        # plugins_pg already refreshes via its own plugin_deleted handler

    pm.plugin_deleted.connect(_on_plugin_deleted)

    window.navigate("home")
    window.resize(1280, 780)
    window.show()

    sys.exit(app.exec())
