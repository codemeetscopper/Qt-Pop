from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from nova.core.plugin_manager import PluginManager
from nova.pages.about_page import AboutPage
from nova.pages.home_page import HomePage
from nova.pages.plugins_page import PluginsPage
from nova.pages.settings_page import SettingsPage
from nova.ui.main_window import MainWindow


def run(qt_pop) -> None:
    app = QApplication.instance() or QApplication(sys.argv)

    # Apply nova.qss
    nova_qss = Path(__file__).parent.parent / "resources" / "qss" / "nova.qss"
    if nova_qss.exists():
        qt_pop.qss.set_style(nova_qss.read_text(encoding="utf-8"))

    # Plugin manager
    plugins_dir = Path(__file__).parent.parent / "plugins"
    pm = PluginManager(qt_pop.data, plugins_dir)

    # Create window
    window = MainWindow(qt_pop, pm)

    # Create pages
    home = HomePage(qt_pop)
    plugins_pg = PluginsPage(pm)
    settings = SettingsPage(qt_pop)
    about = AboutPage(qt_pop)

    window.add_page("home", "Home", "⌂", home)
    window.add_page("plugins", "Plugins", "⚙", plugins_pg)
    window.add_separator()
    window.add_page("settings", "Settings", "≡", settings)
    window.add_page("about", "About", "ℹ", about)

    # Discover + load + start plugins, then add their pages to the window
    for manifest in pm.discover():
        if pm.load(manifest.id):
            pm.start(manifest.id)
            # Create a plugin-specific page and add it to the sidebar
            widget = pm.create_widget(manifest.id)
            if widget is not None:
                window.add_page(
                    f"plugin_{manifest.id}",
                    manifest.name,
                    manifest.icon or "◈",
                    widget,
                )

    # Refresh plugin cards now that everything is loaded
    plugins_pg.refresh()

    # Update home stats whenever a plugin starts or stops
    def _update_home(*_):
        home.update_stats(pm.loaded_count(), pm.active_count())

    pm.plugin_started.connect(_update_home)
    pm.plugin_stopped.connect(_update_home)
    pm.plugin_crashed.connect(_update_home)
    _update_home()

    # Navigate plugin cards to their sidebar page
    plugins_pg.navigate_to_plugin.connect(
        lambda pid: window.navigate(f"plugin_{pid}")
    )

    window.navigate("home")
    window.resize(1280, 780)
    window.show()

    sys.exit(app.exec())
