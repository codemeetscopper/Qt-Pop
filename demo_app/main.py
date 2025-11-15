"""Stacked QtPop showcase application with a custom title bar."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List

from PySide6.QtCore import Qt, QSize, Slot
from PySide6.QtGui import QColor, QClipboard, QGuiApplication, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QPlainTextEdit,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from qtpop import IconCardWidget, QtPop
from qtpop.appearance.stylemanager import StyleManager
from qtpop.configuration.parser import ConfigurationManager
from qtpop.qtpopdatalayer import QtPopDataLayer
from qtpop.qtpoplogger import QtPopLogger
from qtpop.widgets import CustomTitleBar


@dataclass
class NavigationItem:
    title: str
    icon_name: str
    builder: Callable[[], QWidget]


def _contrast_colour(hex_code: str) -> str:
    colour = QColor(hex_code)
    if not colour.isValid():
        return "#000000"
    luminance = (colour.red() * 299 + colour.green() * 587 + colour.blue() * 114) / 1000
    return "#000000" if luminance > 160 else "#ffffff"


class ColourSwatch(QFrame):
    """Simple card showing a palette entry."""

    def __init__(self, title: str, hex_value: str) -> None:
        super().__init__()
        self.setObjectName("ColourSwatch")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setFixedHeight(120)

        self._title = QLabel(title)
        self._title.setObjectName("SwatchTitle")
        self._hex = QLabel(hex_value)
        self._hex.setObjectName("SwatchHex")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        layout.addWidget(self._title)
        layout.addStretch(1)
        layout.addWidget(self._hex, alignment=Qt.AlignLeft | Qt.AlignBottom)

        self.update_colour(hex_value)

    def update_colour(self, hex_value: str) -> None:
        text_colour = _contrast_colour(hex_value)
        border_colour = "rgba(0, 0, 0, 45)" if text_colour == "#ffffff" else "rgba(255, 255, 255, 45)"
        self.setStyleSheet(
            f"background-color: {hex_value};"
            f"color: {text_colour};"
            f"border: 1px solid {border_colour};"
            f"border-radius: 16px;"
        )
        self._hex.setText(hex_value.upper())


class DemoWindow(QMainWindow):
    """Main window demonstrating the QtPop facade via stacked pages."""

    _ICON_SELECTION = [
        "action home",
        "action favorite",
        "action bug report",
        "action face",
        "action lightbulb",
        "action timeline",
        "action visibility",
        "communication alternate email",
        "communication chat",
        "communication support agent",
        "device battery full",
        "device brightness medium",
        "maps u turn left",
        "notification event note",
        "social mood",
    ]

    def __init__(self, qtpop: QtPop, config_path: Path) -> None:
        super().__init__()
        if not qtpop.is_initialized():
            raise RuntimeError("QtPop must be initialised before creating the demo window.")

        self._qtpop = qtpop
        self._config: ConfigurationManager = qtpop.config  # type: ignore[assignment]
        self._style: StyleManager = qtpop.style  # type: ignore[assignment]
        self._icons = qtpop.icon  # type: ignore[assignment]
        self._fonts = qtpop.font  # type: ignore[assignment]
        self._qss = qtpop.qss  # type: ignore[assignment]
        self._data: QtPopDataLayer = qtpop.data  # type: ignore[assignment]
        self._logger: QtPopLogger = qtpop.log  # type: ignore[assignment]

        if not all((self._config, self._style, self._icons, self._fonts, self._qss, self._data, self._logger)):
            raise RuntimeError("QtPop managers failed to initialise correctly.")

        self.setWindowTitle(self._window_title())
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setMinimumSize(1080, 720)

        self._titlebar = CustomTitleBar(qtpop, parent=self, app_name=self._window_title())

        container = QWidget()
        container.setObjectName("DemoContainer")
        root_layout = QVBoxLayout(container)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        root_layout.addWidget(self._titlebar)

        body = QWidget()
        body.setObjectName("DemoBody")
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(24, 24, 24, 24)
        body_layout.setSpacing(24)

        self._navigation = QListWidget()
        self._navigation.setObjectName("DemoNavigation")
        self._navigation.setSpacing(6)
        self._navigation.setMovement(QListWidget.Static)
        self._navigation.setVerticalScrollMode(QListWidget.ScrollPerPixel)
        self._navigation.setFixedWidth(220)

        self._stack = QStackedWidget()
        self._stack.setObjectName("DemoStack")

        body_layout.addWidget(self._navigation)
        body_layout.addWidget(self._stack, 1)
        root_layout.addWidget(body, 1)

        self.setCentralWidget(container)

        self._build_navigation()
        self._connect_signals()
        self._apply_style_updates()

        self._logger.info("QtPop stacked demo ready – configuration loaded from %s", config_path)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------
    def _window_title(self) -> str:
        app_info = self._config.get_value("name")  # type: ignore[assignment]
        version = self._config.get_value("version")  # type: ignore[assignment]
        return f"{getattr(app_info, 'value', app_info)} · QtPop {getattr(version, 'value', version)}"

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _build_navigation(self) -> None:
        items: List[NavigationItem] = [
            NavigationItem("Overview", "action dashboard", self._build_overview_page),
            NavigationItem("Palette & Theme", "device wallpaper", self._build_palette_page),
            NavigationItem("Icon Gallery", "action favorite", self._build_icons_page),
            NavigationItem("Data & Logging", "communication chat", self._build_data_page),
        ]

        for item in items:
            pixmap = self._icons.get_pixmap(item.icon_name, self._style.get_colour("fg1"), 22)
            icon = QIcon(pixmap) if pixmap else QIcon()
            list_item = QListWidgetItem(icon, item.title)
            list_item.setData(Qt.UserRole, item.icon_name)
            list_item.setSizeHint(QSize(200, 48))
            self._navigation.addItem(list_item)
            page = item.builder()
            page.setProperty("nav-title", item.title)
            page.setProperty("nav-icon", item.icon_name)
            self._stack.addWidget(page)

        self._navigation.setCurrentRow(0)
        self._stack.setCurrentIndex(0)

    def _build_overview_page(self) -> QWidget:
        page = QWidget()
        page.setObjectName("DemoPage")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(24)

        hero = QFrame()
        hero.setObjectName("SectionCard")
        hero_layout = QVBoxLayout(hero)
        hero_layout.setContentsMargins(32, 32, 32, 32)
        hero_layout.setSpacing(16)

        title = QLabel("QtPop Feature Showcase")
        title_font = self._fonts.get_font("hero", 28)
        title_font.setPointSize(28)
        title.setFont(title_font)

        subtitle = QLabel(
            "A modular style wrapper for PySide6 with fonts, icons, token-aware QSS "
            "processing and shared runtime utilities."
        )
        subtitle.setWordWrap(True)

        hero_layout.addWidget(title)
        hero_layout.addWidget(subtitle)

        bullet_card = QFrame()
        bullet_card.setObjectName("SectionCard")
        bullet_layout = QVBoxLayout(bullet_card)
        bullet_layout.setContentsMargins(24, 24, 24, 24)
        bullet_layout.setSpacing(12)

        bullets = [
            "Load custom fonts and apply them across widgets via friendly tags.",
            "Tint SVG icons on demand while caching rendered pixmaps.",
            "Replace colour and <img:…> tokens directly in QSS stylesheets.",
            "Share data and configuration updates globally with a signal-powered data layer.",
            "Stream log output into the UI while keeping colourised console output.",
        ]

        for text in bullets:
            line = QLabel(f"• {text}")
            line.setWordWrap(True)
            bullet_layout.addWidget(line)

        layout.addWidget(hero)
        layout.addWidget(bullet_card)
        layout.addStretch(1)
        return page

    def _build_palette_page(self) -> QWidget:
        page = QWidget()
        page.setObjectName("DemoPage")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(24)

        swatch_card = QFrame()
        swatch_card.setObjectName("SectionCard")
        swatch_layout = QVBoxLayout(swatch_card)
        swatch_layout.setContentsMargins(24, 24, 24, 24)
        swatch_layout.setSpacing(16)

        label = QLabel("Active palette")
        label.setObjectName("SectionHeading")
        swatch_layout.addWidget(label)

        self._accent_swatch = ColourSwatch("Accent", self._style.get_colour("accent"))
        self._support_swatch = ColourSwatch("Support", self._style.get_colour("support"))
        self._neutral_swatch = ColourSwatch("Neutral", self._style.get_colour("neutral"))

        grid = QGridLayout()
        grid.setSpacing(16)
        grid.addWidget(self._accent_swatch, 0, 0)
        grid.addWidget(self._support_swatch, 0, 1)
        grid.addWidget(self._neutral_swatch, 1, 0)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        swatch_layout.addLayout(grid)

        controls_card = QFrame()
        controls_card.setObjectName("SectionCard")
        controls_layout = QVBoxLayout(controls_card)
        controls_layout.setContentsMargins(24, 24, 24, 24)
        controls_layout.setSpacing(12)

        description = QLabel(
            "These controls mutate the configuration manager. QtPop refreshes the "
            "StyleManager palette, reapplies tokenised QSS, notifies the data layer "
            "and updates the custom title bar."
        )
        description.setWordWrap(True)
        controls_layout.addWidget(description)

        button_row = QHBoxLayout()
        button_row.setSpacing(12)

        self._accent_button = QPushButton("Cycle accent colour")
        self._accent_button.setObjectName("AccentControl")
        self._accent_button.clicked.connect(self._cycle_accent_colour)

        self._theme_button = QPushButton()
        self._theme_button.setObjectName("ThemeControl")
        self._theme_button.clicked.connect(self._toggle_theme)

        button_row.addWidget(self._accent_button)
        button_row.addWidget(self._theme_button)
        button_row.addStretch(1)

        controls_layout.addLayout(button_row)

        layout.addWidget(swatch_card)
        layout.addWidget(controls_card)
        layout.addStretch(1)
        return page

    def _build_icons_page(self) -> QWidget:
        page = QWidget()
        page.setObjectName("DemoPage")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(24)

        info_card = QFrame()
        info_card.setObjectName("SectionCard")
        info_layout = QVBoxLayout(info_card)
        info_layout.setContentsMargins(24, 24, 24, 16)
        info_layout.setSpacing(12)

        description = QLabel(
            "Icons are rendered from the Material icon set bundled with QtPop. "
            "The gallery recolours previews each time the palette is updated."
        )
        description.setWordWrap(True)
        info_layout.addWidget(description)

        scroll = QScrollArea()
        scroll.setObjectName("IconScroll")
        scroll.setWidgetResizable(True)

        container = QWidget()
        container.setObjectName("IconContainer")
        grid = QGridLayout(container)
        grid.setContentsMargins(24, 24, 24, 24)
        grid.setSpacing(18)
        scroll.setWidget(container)

        self._icon_grid = grid
        self._icon_cards: Dict[str, IconCardWidget] = {}

        layout.addWidget(info_card)
        layout.addWidget(scroll, 1)
        return page

    def _build_data_page(self) -> QWidget:
        page = QWidget()
        page.setObjectName("DemoPage")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(24)

        form_card = QFrame()
        form_card.setObjectName("SectionCard")
        form_layout = QVBoxLayout(form_card)
        form_layout.setContentsMargins(24, 24, 24, 24)
        form_layout.setSpacing(12)

        intro = QLabel(
            "The shared data layer emits signals whenever values change. "
            "Type to publish updates and broadcast them across the demo."
        )
        intro.setWordWrap(True)
        form_layout.addWidget(intro)

        self._data_input = QLineEdit()
        self._data_input.setPlaceholderText("Type to push data through QtPopDataLayer…")
        form_layout.addWidget(self._data_input)

        self._data_echo = QLabel("Shared value: <empty>")
        self._data_echo.setObjectName("DataEcho")
        form_layout.addWidget(self._data_echo)

        broadcast_row = QHBoxLayout()
        broadcast_row.setSpacing(12)

        self._broadcast_button = QPushButton("Broadcast message")
        self._broadcast_button.setObjectName("BroadcastControl")
        broadcast_row.addWidget(self._broadcast_button)

        self._message_label = QLabel("No broadcasts yet")
        self._message_label.setObjectName("MessageLabel")
        broadcast_row.addWidget(self._message_label, 1)

        form_layout.addLayout(broadcast_row)

        log_card = QFrame()
        log_card.setObjectName("SectionCard")
        log_layout = QVBoxLayout(log_card)
        log_layout.setContentsMargins(24, 24, 24, 24)
        log_layout.setSpacing(12)

        log_label = QLabel("Runtime log stream")
        log_layout.addWidget(log_label)

        self._log_view = QPlainTextEdit()
        self._log_view.setReadOnly(True)
        self._log_view.setObjectName("LogView")
        log_layout.addWidget(self._log_view, 1)

        layout.addWidget(form_card)
        layout.addWidget(log_card, 1)
        return page

    # ------------------------------------------------------------------
    # Signal wiring
    # ------------------------------------------------------------------
    def _connect_signals(self) -> None:
        self._navigation.currentRowChanged.connect(self._stack.setCurrentIndex)
        self._navigation.currentRowChanged.connect(self._on_navigation_changed)
        self._data_input.textChanged.connect(self._on_data_input_changed)
        self._broadcast_button.clicked.connect(self._on_broadcast)
        self._data.dataChanged.connect(self._on_shared_data)
        self._data.messageBroadcast.connect(self._on_broadcast_message)
        self._logger.signal.connect(self._append_log)

    def _on_navigation_changed(self, row: int) -> None:
        item = self._stack.widget(row)
        if item:
            title = item.property("nav-title") or self._navigation.item(row).text()
            self._logger.info("Navigated to %s", title)

    def _on_data_input_changed(self, value: str) -> None:
        self._data.set_data("demo.input", value)

    def _on_shared_data(self, key: str, value) -> None:
        if key != "demo.input":
            return
        display = value if value else "<empty>"
        self._data_echo.setText(f"Shared value: {display}")

    def _on_broadcast(self) -> None:
        text = self._data_input.text() or "Hello from QtPop!"
        self._data.broadcast_message("demo.broadcast", text)
        self._logger.info("Broadcasted message: %s", text)

    def _on_broadcast_message(self, channel: str, payload) -> None:
        if channel != "demo.broadcast":
            return
        self._message_label.setText(f"Received: {payload}")

    @Slot(str, str, str, str)
    def _append_log(self, timestamp: str, message: str, level: str, colour: str) -> None:
        text = f"[{timestamp}] {level:<8} {message}"
        self._log_view.appendPlainText(text)

    # ------------------------------------------------------------------
    # Styling & data helpers
    # ------------------------------------------------------------------
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

    def _apply_style_updates(self) -> None:
        accent = self._config.get_value("accent").value  # type: ignore[union-attr]
        support = self._config.get_value("support").value  # type: ignore[union-attr]
        neutral = self._config.get_value("neutral").value  # type: ignore[union-attr]
        theme = self._config.get_value("theme").value  # type: ignore[union-attr]

        self._style.initialise(accent, support, neutral, str(theme))
        self._qss.set_style()
        self._data.update_style(str(theme))

        try:
            qss_setting = self._config.get_value("qss_path")  # type: ignore[assignment]
            qss_path = getattr(qss_setting, "value", qss_setting)
        except Exception:
            qss_path = None

        self._data.update_config({
            "accent": accent,
            "support": support,
            "neutral": neutral,
            "theme": str(theme),
            "qss_path": qss_path,
        })

        self._refresh_palette_swatches()
        self._populate_icon_gallery()
        self._update_theme_button_text()
        self._titlebar.refresh_palette()
        self._refresh_navigation_icons()

    def _refresh_palette_swatches(self) -> None:
        self._accent_swatch.update_colour(self._style.get_colour("accent"))
        self._support_swatch.update_colour(self._style.get_colour("support"))
        self._neutral_swatch.update_colour(self._style.get_colour("neutral"))

    def _refresh_navigation_icons(self) -> None:
        colour = self._style.get_colour("fg1")
        for index in range(self._navigation.count()):
            item = self._navigation.item(index)
            icon_name = item.data(Qt.UserRole)
            if not icon_name:
                continue
            pixmap = self._icons.get_pixmap(icon_name, colour, 22)
            item.setIcon(QIcon(pixmap) if pixmap else QIcon())

    def _populate_icon_gallery(self) -> None:
        tint = self._style.get_colour("accent")
        clipboard: QClipboard = QGuiApplication.clipboard()

        while self._icon_grid.count():
            item = self._icon_grid.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        self._icon_cards.clear()

        row = col = 0
        for name in self._ICON_SELECTION:
            pixmap = self._icons.get_pixmap(name, tint, 48)
            card = IconCardWidget(name, pixmap, size=48)
            card.copy_requested.connect(lambda text, clip=clipboard: clip.setText(text))
            self._icon_cards[name] = card
            self._icon_grid.addWidget(card, row, col)
            col += 1
            if col >= 3:
                col = 0
                row += 1

    def _update_theme_button_text(self) -> None:
        theme = str(self._config.get_value("theme").value).lower()  # type: ignore[union-attr]
        if theme == "dark":
            self._theme_button.setText("Switch to light theme")
        else:
            self._theme_button.setText("Switch to dark theme")


def main() -> None:
    app = QApplication(sys.argv)

    config_path = Path(__file__).resolve().parent / "config" / "demo_config.json"
    qtpop = QtPop.instance().initialise(config_path)

    window = DemoWindow(qtpop, config_path)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
