"""Tabbed QtPop showcase application mirroring the full-featured app."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, List

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QClipboard, QGuiApplication, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSplitter,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from app.widgets.addfontcard import AddFontCard
from app.widgets.fontcard import FontCard
from app.widgets.iconbrowser import IconBrowserWidget
from app.widgets.loggingwindow import QLogWidget
from app.widgets.settingsitemwidget import SettingItemWidget
from qtpop import QtPop
from qtpop.appearance.stylemanager import StyleManager
from qtpop.configuration.models import SettingItem
from qtpop.configuration.parser import ConfigurationManager
from qtpop.qtpopdatalayer import QtPopDataLayer
from qtpop.qtpoplogger import QtPopLogger
from qtpop.widgets import CustomTitleBar


class ColourSwatch(QFrame):
    """Compact palette preview tile."""

    def __init__(self, title: str, colour: str) -> None:
        super().__init__()
        self.setObjectName("ColourSwatch")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self._title = QLabel(title)
        self._title.setObjectName("SwatchTitle")
        self._hex = QLabel(colour.upper())
        self._hex.setObjectName("SwatchHex")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(6)
        layout.addWidget(self._title)
        layout.addStretch(1)
        layout.addWidget(self._hex)

        self.update_colour(colour)

    def update_colour(self, hex_colour: str) -> None:
        colour = QColor(hex_colour)
        if not colour.isValid():
            colour = QColor("#000000")
        luminance = (colour.red() * 299 + colour.green() * 587 + colour.blue() * 114) / 1000
        text_colour = "#000000" if luminance > 160 else "#ffffff"
        border_colour = "rgba(0, 0, 0, 40)" if luminance > 160 else "rgba(255, 255, 255, 45)"
        self.setStyleSheet(
            f"background-color: {colour.name()};"
            f"color: {text_colour};"
            f"border: 1px solid {border_colour};"
            f"border-radius: 16px;"
        )
        self._hex.setText(colour.name().upper())


class DemoWindow(QMainWindow):
    """Professional, simplified demonstration window that mirrors the full app."""

    def __init__(self, qtpop: QtPop, config_path: Path) -> None:
        super().__init__()
        if not qtpop.is_initialized():
            raise RuntimeError("QtPop must be initialised before creating the demo window.")

        self._qtpop = qtpop
        self._config_path = config_path
        self._config: ConfigurationManager = qtpop.config  # type: ignore[assignment]
        self._style: StyleManager = qtpop.style  # type: ignore[assignment]
        self._icons = qtpop.icon  # type: ignore[assignment]
        self._fonts = qtpop.font  # type: ignore[assignment]
        self._qss = qtpop.qss  # type: ignore[assignment]
        self._data: QtPopDataLayer = qtpop.data  # type: ignore[assignment]
        self._logger: QtPopLogger = qtpop.log  # type: ignore[assignment]

        if not all((self._config, self._style, self._icons, self._fonts, self._qss, self._data, self._logger)):
            raise RuntimeError("QtPop managers failed to initialise correctly.")

        self._titlebar = CustomTitleBar(qtpop, parent=self, app_name=self._window_title())
        self._tab_widget: QTabWidget | None = None
        self._accent_swatch: ColourSwatch | None = None
        self._support_swatch: ColourSwatch | None = None
        self._neutral_swatch: ColourSwatch | None = None
        self._accent_button: QPushButton | None = None
        self._theme_button: QPushButton | None = None
        self._qss_input: QPlainTextEdit | None = None
        self._qss_output: QPlainTextEdit | None = None
        self._settings_widgets: List[SettingItemWidget] = []
        self._font_list: QListWidget | None = None
        self._icon_browser: IconBrowserWidget | None = None
        self._log_widget: QLogWidget | None = None
        self._data_input: QLineEdit | None = None
        self._data_echo: QLabel | None = None
        self._broadcast_button: QPushButton | None = None
        self._message_label: QLabel | None = None

        self._register_default_fonts()
        self._build_ui()
        self._connect_signals()
        self._apply_style_updates()

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setMinimumSize(1180, 760)
        self.setWindowTitle(self._window_title())
        self._logger.info("QtPop demo window ready – configuration loaded from %s", config_path)

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _window_title(self) -> str:
        name = self._config.get_value("name")  # type: ignore[assignment]
        version = self._config.get_value("version")  # type: ignore[assignment]
        return f"{getattr(name, 'value', name)} · QtPop {getattr(version, 'value', version)}"

    def _build_ui(self) -> None:
        container = QWidget()
        container.setObjectName("DemoContainer")
        root_layout = QVBoxLayout(container)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        root_layout.addWidget(self._titlebar)

        content = QWidget()
        content.setObjectName("DemoContent")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(32, 32, 32, 32)
        content_layout.setSpacing(24)

        header_card = QFrame()
        header_card.setObjectName("HeaderCard")
        header_layout = QVBoxLayout(header_card)
        header_layout.setContentsMargins(28, 24, 28, 24)
        header_layout.setSpacing(8)

        title_label = QLabel(self._window_title())
        title_label.setObjectName("HeaderTitle")
        subtitle = QLabel(
            "A compact, professional dashboard that surfaces every capability of the full QtPop app."
        )
        subtitle.setWordWrap(True)
        subtitle.setObjectName("HeaderSubtitle")

        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle)

        self._tab_widget = QTabWidget()
        self._tab_widget.setObjectName("DemoTabs")
        self._tab_widget.setDocumentMode(True)
        self._tab_widget.setTabPosition(QTabWidget.North)

        content_layout.addWidget(header_card)
        content_layout.addWidget(self._tab_widget, 1)

        root_layout.addWidget(content, 1)
        self.setCentralWidget(container)

        self._populate_tabs()

    def _populate_tabs(self) -> None:
        assert self._tab_widget is not None
        self._tab_widget.clear()

        tabs = [
            ("Overview", "action dashboard", self._build_overview_tab),
            ("Palette", "device wallpaper", self._build_palette_tab),
            ("Settings", "action tune", self._build_settings_tab),
            ("QSS Studio", "action code", self._build_qss_tab),
            ("Typography", "editor format size", self._build_fonts_tab),
            ("Icons", "action favorite", self._build_icons_tab),
            ("Diagnostics", "communication chat", self._build_diagnostics_tab),
        ]

        for title, icon_name, builder in tabs:
            page = builder()
            self._tab_widget.addTab(page, title)
            page.setProperty("nav-icon", icon_name)

        self._update_tab_icons()

    def _card(self, parent: QWidget | None = None) -> QFrame:
        card = QFrame(parent)
        card.setObjectName("SectionCard")
        return card

    def _build_overview_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(24)

        hero = self._card()
        hero_layout = QVBoxLayout(hero)
        hero_layout.setContentsMargins(32, 32, 32, 32)
        hero_layout.setSpacing(12)

        title = QLabel("QtPop Feature Showcase")
        title.setObjectName("HeroTitle")
        description = QLabel(
            "Explore fonts, palette controls, QSS token processing, icon tinting, configuration editing, "
            "and realtime logging—all powered by the QtPop facade."
        )
        description.setWordWrap(True)

        hero_layout.addWidget(title)
        hero_layout.addWidget(description)

        bullets = self._card()
        bullets_layout = QVBoxLayout(bullets)
        bullets_layout.setContentsMargins(24, 24, 24, 24)
        bullets_layout.setSpacing(10)

        for line in (
            "Flexible configuration management with group-aware editors.",
            "Token-aware QSS processing with live preview and application.",
            "Dynamic palette tweaks and theme toggling via the StyleManager.",
            "On-demand font loading, tagging, and application.",
            "Cached Material icon gallery with instant recolouring.",
            "Structured runtime logging streamed through Qt signals.",
        ):
            label = QLabel(f"• {line}")
            label.setWordWrap(True)
            bullets_layout.addWidget(label)

        layout.addWidget(hero)
        layout.addWidget(bullets)
        layout.addStretch(1)
        return page

    def _build_palette_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(24)

        swatch_card = self._card()
        swatch_layout = QVBoxLayout(swatch_card)
        swatch_layout.setContentsMargins(24, 24, 24, 24)
        swatch_layout.setSpacing(18)

        label = QLabel("Active palette")
        label.setObjectName("SectionHeading")
        swatch_layout.addWidget(label)

        grid = QGridLayout()
        grid.setSpacing(18)

        self._accent_swatch = ColourSwatch("Accent", self._style.get_colour("accent"))
        self._support_swatch = ColourSwatch("Support", self._style.get_colour("support"))
        self._neutral_swatch = ColourSwatch("Neutral", self._style.get_colour("neutral"))

        grid.addWidget(self._accent_swatch, 0, 0)
        grid.addWidget(self._support_swatch, 0, 1)
        grid.addWidget(self._neutral_swatch, 1, 0)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)

        swatch_layout.addLayout(grid)

        controls_card = self._card()
        controls_layout = QVBoxLayout(controls_card)
        controls_layout.setContentsMargins(24, 24, 24, 24)
        controls_layout.setSpacing(14)

        description = QLabel(
            "Adjust values stored in the configuration manager. QtPop refreshes the palette, re-applies "
            "QSS tokens, updates the custom title bar, and notifies the shared data layer."
        )
        description.setWordWrap(True)
        controls_layout.addWidget(description)

        button_row = QHBoxLayout()
        button_row.setSpacing(12)

        self._accent_button = QPushButton("Cycle accent colour")
        self._accent_button.setObjectName("AccentControl")
        self._theme_button = QPushButton()
        self._theme_button.setObjectName("ThemeControl")

        button_row.addWidget(self._accent_button)
        button_row.addWidget(self._theme_button)
        button_row.addStretch(1)

        controls_layout.addLayout(button_row)

        layout.addWidget(swatch_card)
        layout.addWidget(controls_card)
        layout.addStretch(1)
        return page

    def _build_settings_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(24)

        instructions = self._card()
        instructions_layout = QVBoxLayout(instructions)
        instructions_layout.setContentsMargins(24, 24, 24, 24)
        instructions_layout.setSpacing(10)

        heading = QLabel("Configuration editor")
        heading.setObjectName("SectionHeading")
        blurb = QLabel(
            "User settings are grouped by their configured category. Static metadata remains available "
            "for quick reference. Adjust any value and press save to persist and refresh the UI."
        )
        blurb.setWordWrap(True)

        instructions_layout.addWidget(heading)
        instructions_layout.addWidget(blurb)

        editor_card = self._card()
        editor_layout = QVBoxLayout(editor_card)
        editor_layout.setContentsMargins(0, 0, 0, 0)
        editor_layout.setSpacing(0)

        tabs = QTabWidget()
        tabs.setObjectName("SettingsTabs")
        self._settings_widgets = []

        grouped: Dict[str, List[SettingItem]] = {}
        for item in self._config.data.configuration.user.values():  # type: ignore[union-attr]
            grouped.setdefault(item.group, []).append(item)

        for group_name, items in grouped.items():
            tabs.addTab(self._settings_group_page(items), group_name)

        static_items = []
        for key, value in self._config.data.configuration.static.items():  # type: ignore[union-attr]
            static_items.append(SettingItem(key, key, value, [], "Application static setting", "text", "user", "Static", ""))
        tabs.addTab(self._settings_group_page(static_items, static=True), "Static")

        editor_layout.addWidget(tabs)

        footer = QHBoxLayout()
        footer.setContentsMargins(24, 16, 24, 24)
        footer.setSpacing(12)
        footer.addStretch(1)
        save_button = QPushButton("Save settings")
        save_button.setObjectName("SaveSettingsButton")
        footer.addWidget(save_button)
        editor_layout.addLayout(footer)

        save_button.clicked.connect(self._save_settings)

        layout.addWidget(instructions)
        layout.addWidget(editor_card, 1)
        return page

    def _settings_group_page(self, items: List[SettingItem], static: bool = False) -> QWidget:
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setObjectName("SettingsScroll")

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(24, 24, 24, 24)
        content_layout.setSpacing(12)

        for item in items:
            widget = SettingItemWidget(item)
            widget.setObjectName("SettingItem")
            content_layout.addWidget(widget)
            if not static:
                self._settings_widgets.append(widget)

        content_layout.addStretch(1)
        scroll.setWidget(content)
        container_layout.addWidget(scroll)
        return container

    def _build_qss_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(24)

        studio_card = self._card()
        studio_layout = QVBoxLayout(studio_card)
        studio_layout.setContentsMargins(24, 24, 24, 24)
        studio_layout.setSpacing(16)

        heading = QLabel("QSS Studio")
        heading.setObjectName("SectionHeading")
        intro = QLabel(
            "Edit the raw stylesheet on the left, preview the processed output on the right, and apply it to "
            "the running application—complete with colour and <img:…> token resolution."
        )
        intro.setWordWrap(True)

        studio_layout.addWidget(heading)
        studio_layout.addWidget(intro)

        splitter = QSplitter()
        splitter.setOrientation(Qt.Horizontal)

        self._qss_input = QPlainTextEdit()
        self._qss_input.setObjectName("QssInput")
        self._qss_output = QPlainTextEdit()
        self._qss_output.setObjectName("QssOutput")
        self._qss_output.setReadOnly(True)

        splitter.addWidget(self._qss_input)
        splitter.addWidget(self._qss_output)
        splitter.setSizes([600, 600])

        studio_layout.addWidget(splitter, 1)

        button_row = QHBoxLayout()
        button_row.setSpacing(12)
        load_button = QPushButton("Load from file…")
        apply_button = QPushButton("Apply style")
        copy_button = QPushButton("Copy processed")

        button_row.addWidget(load_button)
        button_row.addWidget(apply_button)
        button_row.addWidget(copy_button)
        button_row.addStretch(1)

        studio_layout.addLayout(button_row)

        load_button.clicked.connect(self._load_qss_from_dialog)
        apply_button.clicked.connect(self._apply_qss_from_editor)
        copy_button.clicked.connect(self._copy_processed_qss)

        layout.addWidget(studio_card, 1)
        self._load_qss_into_editor()
        return page

    def _build_fonts_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(24)

        card = self._card()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 24, 24, 24)
        card_layout.setSpacing(16)

        heading = QLabel("Loaded font tags")
        heading.setObjectName("SectionHeading")
        card_layout.addWidget(heading)

        self._font_list = QListWidget()
        self._font_list.setObjectName("FontList")
        self._font_list.setSpacing(8)
        self._font_list.setUniformItemSizes(False)
        self._font_list.setVerticalScrollMode(QListWidget.ScrollPerPixel)

        card_layout.addWidget(self._font_list, 1)
        layout.addWidget(card, 1)

        self._refresh_font_list()
        return page

    def _build_icons_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(24)

        card = self._card()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(12, 12, 12, 12)
        card_layout.setSpacing(12)

        icon_setting = self._config.get_value("icon_path")
        icon_path = Path(getattr(icon_setting, "value", icon_setting))
        if not icon_path.is_absolute():
            icon_path = (self._config_path.parent / icon_path).resolve()
        self._icon_browser = IconBrowserWidget(qt_pop=self._qtpop, images_path=str(icon_path))
        self._icon_browser.setObjectName("IconBrowser")
        card_layout.addWidget(self._icon_browser)

        layout.addWidget(card, 1)
        return page

    def _build_diagnostics_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(24)

        data_card = self._card()
        data_layout = QVBoxLayout(data_card)
        data_layout.setContentsMargins(24, 24, 24, 24)
        data_layout.setSpacing(14)

        heading = QLabel("Shared data layer")
        heading.setObjectName("SectionHeading")
        data_layout.addWidget(heading)

        description = QLabel(
            "The global data layer emits Qt signals whenever values change. Type to publish updates or "
            "broadcast structured messages to listening components."
        )
        description.setWordWrap(True)
        data_layout.addWidget(description)

        self._data_input = QLineEdit()
        self._data_input.setPlaceholderText("Type to update demo.input …")
        data_layout.addWidget(self._data_input)

        self._data_echo = QLabel("Shared value: <empty>")
        self._data_echo.setObjectName("DataEcho")
        data_layout.addWidget(self._data_echo)

        row = QHBoxLayout()
        row.setSpacing(12)
        self._broadcast_button = QPushButton("Broadcast message")
        self._broadcast_button.setObjectName("BroadcastControl")
        row.addWidget(self._broadcast_button)
        self._message_label = QLabel("No broadcasts yet")
        self._message_label.setObjectName("MessageLabel")
        row.addWidget(self._message_label, 1)
        data_layout.addLayout(row)

        log_card = self._card()
        log_layout = QVBoxLayout(log_card)
        log_layout.setContentsMargins(12, 12, 12, 12)
        log_layout.setSpacing(8)

        log_heading = QLabel("Runtime log stream")
        log_heading.setObjectName("SectionHeading")
        log_layout.addWidget(log_heading)

        self._log_widget = QLogWidget(self._qtpop)
        log_layout.addWidget(self._log_widget, 1)

        layout.addWidget(data_card)
        layout.addWidget(log_card, 1)
        return page

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _register_default_fonts(self) -> None:
        root = Path(__file__).resolve().parents[1] / "resources" / "fonts"
        try:
            self._fonts.load_font(str(root / "RobotoCondensed-VariableFont_wght.ttf"), "h1", 18)
            self._fonts.load_font(str(root / "RobotoCondensed-VariableFont_wght.ttf"), "h2", 14)
            self._fonts.load_font(str(root / "Roboto-VariableFont_wdth,wght.ttf"), "p", 11)
            self._fonts.load_font(str(root / "RobotoCondensed-VariableFont_wght.ttf"), "pc", 10)
            self._fonts.load_font(str(root / "Inconsolata-VariableFont_wdth,wght.ttf"), "log", 11)
            self._fonts.load_font(str(root / "JollyLodger-Regular.ttf"), "style", 12)
        except Exception as exc:  # pragma: no cover - depends on font availability
            self._logger.warning("Failed to register default fonts: %s", exc)

    def _connect_signals(self) -> None:
        if self._tab_widget:
            self._tab_widget.currentChanged.connect(self._on_tab_changed)
        if self._accent_button:
            self._accent_button.clicked.connect(self._cycle_accent_colour)
        if self._theme_button:
            self._theme_button.clicked.connect(self._toggle_theme)
        if self._data_input:
            self._data_input.textChanged.connect(self._on_data_input_changed)
        if self._broadcast_button:
            self._broadcast_button.clicked.connect(self._on_broadcast)
        self._data.dataChanged.connect(self._on_shared_data)
        self._data.messageBroadcast.connect(self._on_broadcast_message)
        if self._log_widget:
            self._log_widget.connect_logger(self._logger.signal)

    def _apply_style_updates(self) -> None:
        accent = self._config.get_value("accent").value  # type: ignore[union-attr]
        support = self._config.get_value("support").value  # type: ignore[union-attr]
        neutral = self._config.get_value("neutral").value  # type: ignore[union-attr]
        theme = str(self._config.get_value("theme").value).lower()  # type: ignore[union-attr]

        self._style.initialise(accent, support, neutral, theme)
        stylesheet = self._qss_input.toPlainText() if self._qss_input else self._load_qss_text()
        self._qss.set_style(stylesheet)
        self._data.update_style(theme)
        qss_setting = self._config.get_value("qss_path")  # type: ignore[assignment]
        qss_value = getattr(qss_setting, "value", qss_setting)
        self._data.update_config({
            "accent": accent,
            "support": support,
            "neutral": neutral,
            "theme": theme,
            "qss_path": qss_value,
        })

        self._refresh_palette_swatches()
        self._update_theme_button_text()
        self._update_tab_icons()
        self._titlebar.refresh_palette()
        self._refresh_icon_browser()
        self._refresh_font_list()
        self._update_processed_qss()

    def _refresh_icon_browser(self) -> None:
        if not self._icon_browser:
            return
        colour_map = self._style.colour_map()
        current = self._icon_browser.color_combo.currentText()
        self._icon_browser.color_combo.blockSignals(True)
        self._icon_browser.color_combo.clear()
        for name, colour in colour_map.items():
            self._icon_browser.color_combo.addItem(name, colour)
        self._icon_browser.color_combo.blockSignals(False)
        target = current if current in colour_map else "accent"
        if target in colour_map:
            self._icon_browser.color_combo.setCurrentText(target)
        elif colour_map:
            self._icon_browser.color_combo.setCurrentIndex(0)

    def _refresh_palette_swatches(self) -> None:
        if self._accent_swatch:
            self._accent_swatch.update_colour(self._style.get_colour("accent"))
        if self._support_swatch:
            self._support_swatch.update_colour(self._style.get_colour("support"))
        if self._neutral_swatch:
            self._neutral_swatch.update_colour(self._style.get_colour("neutral"))

    def _update_theme_button_text(self) -> None:
        if not self._theme_button:
            return
        theme = str(self._config.get_value("theme").value).lower()  # type: ignore[union-attr]
        self._theme_button.setText("Switch to light theme" if theme == "dark" else "Switch to dark theme")

    def _update_tab_icons(self) -> None:
        if not self._tab_widget:
            return
        tint = self._style.get_colour("fg1")
        for index in range(self._tab_widget.count()):
            widget = self._tab_widget.widget(index)
            icon_name = widget.property("nav-icon")
            if not icon_name:
                continue
            pixmap = self._icons.get_pixmap(icon_name, tint, 22)
            self._tab_widget.setTabIcon(index, QIcon(pixmap) if pixmap else QIcon())

    def _refresh_font_list(self) -> None:
        if not self._font_list:
            return
        self._font_list.clear()
        add_card = AddFontCard(self._on_add_font)
        add_card.setObjectName("FontCardFrame")
        add_item = QListWidgetItem()
        add_item.setSizeHint(add_card.sizeHint())
        self._font_list.addItem(add_item)
        self._font_list.setItemWidget(add_item, add_card)

        for tag, info in self._fonts.get_font_map().items():
            card = FontCard(info["family"], tag, info["size"], self._apply_font_tag)
            card.setObjectName("FontCardFrame")
            item = QListWidgetItem()
            hint = card.sizeHint()
            hint.setHeight(hint.height() + 12)
            item.setSizeHint(hint)
            self._font_list.addItem(item)
            self._font_list.setItemWidget(item, card)

    def _on_add_font(self, path: str, tag: str, size: int) -> None:
        try:
            self._fonts.load_font(path, tag, size)
            self._logger.info("Loaded custom font %s with tag %s", path, tag)
            self._refresh_font_list()
        except Exception as exc:  # pragma: no cover - depends on file dialog
            self._logger.error("Failed to load font %s: %s", path, exc)

    def _apply_font_tag(self, tag: str, size: int | None = None) -> None:
        font = self._fonts.get_font(tag)
        if size is not None:
            font.setPointSize(size)
        app = QApplication.instance()
        if app:
            app.setFont(font)
        self._apply_style_updates()

    def _load_qss_into_editor(self) -> None:
        if not self._qss_input:
            return
        self._qss_input.blockSignals(True)
        self._qss_input.setPlainText(self._load_qss_text())
        self._qss_input.blockSignals(False)
        self._update_processed_qss()

    def _update_processed_qss(self) -> None:
        if not (self._qss_input and self._qss_output):
            return
        processed = self._qss.process(self._qss_input.toPlainText())
        self._qss_output.setPlainText(processed)

    def _load_qss_text(self) -> str:
        setting = self._config.get_value("qss_path")  # type: ignore[assignment]
        value = getattr(setting, "value", setting)
        path = Path(value)
        if not path.is_absolute():
            path = (self._config_path.parent / value).resolve()
        try:
            return path.read_text(encoding="utf-8")
        except Exception as exc:
            self._logger.warning("Failed to read QSS file %s: %s", path, exc)
            return ""

    def _load_qss_from_dialog(self) -> None:
        if not self._qss_input:
            return
        file_path, _ = QFileDialog.getOpenFileName(self, "Open QSS File", str(self._config_path.parent), "QSS Files (*.qss)")
        if not file_path:
            return
        try:
            text = Path(file_path).read_text(encoding="utf-8")
        except Exception as exc:  # pragma: no cover - user interaction
            self._logger.error("Failed to load QSS file %s: %s", file_path, exc)
            return
        self._qss_input.setPlainText(text)
        self._update_processed_qss()

    def _apply_qss_from_editor(self) -> None:
        if not self._qss_input:
            return
        raw = self._qss_input.toPlainText()
        self._qss.set_style(raw)
        self._update_processed_qss()
        self._logger.info("Applied QSS from editor.")

    def _copy_processed_qss(self) -> None:
        if not (self._qss_output and QGuiApplication.instance()):
            return
        clipboard: QClipboard = QGuiApplication.clipboard()
        clipboard.setText(self._qss_output.toPlainText())
        self._logger.info("Copied processed QSS to clipboard.")

    def _save_settings(self) -> None:
        for widget in self._settings_widgets:
            item = widget.item
            self._config.set_value(item.shortname, item.value)
        if hasattr(self._config, "save"):
            self._config.save()
        self._logger.info("Settings saved. Applying updates…")
        self._apply_style_updates()

    # ------------------------------------------------------------------
    # Data and logging
    # ------------------------------------------------------------------
    def _on_tab_changed(self, index: int) -> None:
        if not self._tab_widget:
            return
        title = self._tab_widget.tabText(index)
        self._logger.info("Switched to tab: %s", title)

    def _on_data_input_changed(self, value: str) -> None:
        self._data.set_data("demo.input", value)

    def _on_shared_data(self, key: str, value) -> None:
        if key != "demo.input" or not self._data_echo:
            return
        display = value if value else "<empty>"
        self._data_echo.setText(f"Shared value: {display}")

    def _on_broadcast(self) -> None:
        if not self._data_input:
            return
        text = self._data_input.text() or "Hello from QtPop!"
        self._data.broadcast_message("demo.broadcast", text)
        self._logger.info("Broadcasted message: %s", text)

    def _on_broadcast_message(self, channel: str, payload) -> None:
        if channel != "demo.broadcast" or not self._message_label:
            return
        self._message_label.setText(f"Received: {payload}")

    def _cycle_accent_colour(self) -> None:
        setting = self._config.get_value("accent")  # type: ignore[assignment]
        current = getattr(setting, "value", "")
        palette = getattr(setting, "values", []) or [current]
        try:
            index = palette.index(current)
        except ValueError:
            index = -1
        new_value = palette[(index + 1) % len(palette)] if palette else current
        self._config.set_value("accent", new_value)
        setting.value = new_value
        self._logger.info("Accent colour changed to %s", new_value)
        self._apply_style_updates()

    def _toggle_theme(self) -> None:
        setting = self._config.get_value("theme")  # type: ignore[assignment]
        current = str(getattr(setting, "value", "light")).lower()
        new_value = "dark" if current == "light" else "light"
        self._config.set_value("theme", new_value)
        setting.value = new_value
        self._logger.info("Theme toggled to %s mode", new_value)
        self._apply_style_updates()


def main() -> None:
    app = QApplication(sys.argv)
    config_path = Path(__file__).resolve().parent / "config" / "demo_config.json"
    qtpop = QtPop.instance().initialise(config_path)
    window = DemoWindow(qtpop, config_path)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
