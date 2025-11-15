"""Executable showcase application for the QtPop style wrapper."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import List

from PySide6.QtCore import Qt, QSize, Slot
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
)

from qtpop import QtPop
from qtpop.appearance.stylemanager import StyleManager
from qtpop.configuration.parser import ConfigurationManager
from qtpop.qtpopdatalayer import QtPopDataLayer
from qtpop.qtpoplogger import QtPopLogger


class DemoWindow(QMainWindow):
    """Main window wiring together each QtPop subsystem."""

    _ICON_NAMES: List[str] = [
        "action_accessibility",
        "action_account_circle",
        "action_alarm",
        "action_bug_report",
        "action_face",
        "action_thumb_up",
        "device_battery_full",
        "notification_event_note",
        "social_mood"
    ]

    def __init__(self, qtpop: QtPop, config_path: Path) -> None:
        super().__init__()
        if not qtpop.is_initialized():
            raise RuntimeError("QtPop must be initialised before creating the demo window.")

        self._qtpop = qtpop
        self._config: ConfigurationManager = qtpop.config  # type: ignore[assignment]
        self._icons = qtpop.icon  # type: ignore[assignment]
        self._fonts = qtpop.font  # type: ignore[assignment]
        self._style: StyleManager = qtpop.style  # type: ignore[assignment]
        self._data: QtPopDataLayer = qtpop.data  # type: ignore[assignment]
        self._qss = qtpop.qss  # type: ignore[assignment]
        self._logger: QtPopLogger = qtpop.log  # type: ignore[assignment]

        if not all((self._config, self._icons, self._fonts, self._style, self._data, self._qss, self._logger)):
            raise RuntimeError("QtPop managers failed to initialise correctly.")

        self.setWindowTitle(self._window_title())
        self.resize(960, 720)

        root = QWidget(self)
        root.setObjectName("RootPanel")
        layout = QVBoxLayout(root)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        self._palette_group = self._create_palette_group()
        self._icon_group = self._create_icon_group()
        self._data_group = self._create_data_group()
        self._logger_group = self._create_logger_group()

        layout.addWidget(self._palette_group)
        layout.addWidget(self._icon_group)
        layout.addWidget(self._data_group)
        layout.addWidget(self._logger_group)
        layout.addStretch(1)

        self.setCentralWidget(root)

        self._connect_signals()
        self._refresh_palette_swatches()
        self._populate_icon_list()
        self._update_theme_button_text()

        self._logger.info("QtPop demo window ready – configuration loaded from %s", config_path)

    # ------------------------------------------------------------------
    # UI construction helpers
    # ------------------------------------------------------------------
    def _create_palette_group(self) -> QGroupBox:
        group = QGroupBox("Palette, fonts and QSS tokens")
        layout = QVBoxLayout(group)
        layout.setSpacing(10)

        heading = QLabel(self._window_title())
        heading.setWordWrap(True)
        heading.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        heading.setFont(self._fonts.get_font("heading", 26))  # type: ignore[arg-type]

        description = QLabel(
            "QtPop loads fonts, theme colours and the demo QSS. "
            "Use the buttons below to cycle palette values and inspect the live styling."
        )
        description.setWordWrap(True)

        layout.addWidget(heading)
        layout.addWidget(description)

        swatch_row = QHBoxLayout()
        swatch_row.setSpacing(8)
        self._accent_label = self._build_colour_label("Accent", "accent")
        self._support_label = self._build_colour_label("Support", "support")
        self._neutral_label = self._build_colour_label("Neutral", "neutral")

        swatch_row.addWidget(self._accent_label)
        swatch_row.addWidget(self._support_label)
        swatch_row.addWidget(self._neutral_label)
        swatch_row.addStretch(1)

        icon_row = QHBoxLayout()
        icon_row.setSpacing(12)
        accent_icon = QLabel()
        accent_icon.setObjectName("AccentIcon")
        accent_icon.setFixedSize(56, 56)
        support_icon = QLabel()
        support_icon.setObjectName("SupportIcon")
        support_icon.setFixedSize(56, 56)

        icon_caption = QLabel("Icon tokens are rendered via the QSS manager using temporary SVGs.")
        icon_caption.setWordWrap(True)

        icon_row.addWidget(accent_icon)
        icon_row.addWidget(support_icon)
        icon_row.addWidget(icon_caption, 1)

        button_row = QHBoxLayout()
        button_row.setSpacing(8)
        self._accent_button = QPushButton("Cycle accent colour")
        self._accent_button.setObjectName("AccentButton")
        self._accent_button.clicked.connect(self._cycle_accent_colour)

        self._theme_button = QPushButton()
        self._theme_button.setObjectName("SupportButton")
        self._theme_button.clicked.connect(self._toggle_theme)

        button_row.addWidget(self._accent_button)
        button_row.addWidget(self._theme_button)
        button_row.addStretch(1)

        layout.addLayout(swatch_row)
        layout.addLayout(icon_row)
        layout.addLayout(button_row)
        return group

    def _create_icon_group(self) -> QGroupBox:
        group = QGroupBox("Icon manager showcase")
        layout = QVBoxLayout(group)
        layout.setSpacing(8)

        label = QLabel(
            "Icons are colourised on demand using the StyleManager palette. "
            "Search heuristics allow partial icon names."
        )
        label.setWordWrap(True)
        layout.addWidget(label)

        self._icon_list = QListWidget()
        self._icon_list.setViewMode(QListWidget.IconMode)
        self._icon_list.setResizeMode(QListWidget.Adjust)
        self._icon_list.setMovement(QListWidget.Static)
        self._icon_list.setIconSize(QSize(48, 48))
        self._icon_list.setSpacing(12)

        layout.addWidget(self._icon_list)
        return group

    def _create_data_group(self) -> QGroupBox:
        group = QGroupBox("Shared data and messaging")
        layout = QVBoxLayout(group)
        layout.setSpacing(8)

        label = QLabel(
            "QtPopDataLayer provides cross-widget signals. "
            "Typing updates the shared store and emits dataChanged events."
        )
        label.setWordWrap(True)
        layout.addWidget(label)

        self._data_input = QLineEdit()
        self._data_input.setPlaceholderText("Type to push data through QtPopDataLayer…")
        layout.addWidget(self._data_input)

        self._data_echo = QLabel("Shared value: <empty>")
        layout.addWidget(self._data_echo)

        self._message_label = QLabel("Last broadcast: <none>")
        self._message_label.setObjectName("MessageLabel")
        layout.addWidget(self._message_label)

        button_row = QHBoxLayout()
        button_row.setSpacing(8)

        self._broadcast_button = QPushButton("Broadcast message")
        self._broadcast_button.setObjectName("SupportButton")
        self._broadcast_button.clicked.connect(self._broadcast_message)
        button_row.addWidget(self._broadcast_button)
        button_row.addStretch(1)

        layout.addLayout(button_row)
        return group

    def _create_logger_group(self) -> QGroupBox:
        group = QGroupBox("Logger output")
        layout = QVBoxLayout(group)
        layout.setSpacing(8)

        label = QLabel(
            "QtPopLogger emits Qt signals for log handlers. "
            "Press the button to push structured entries into the view."
        )
        label.setWordWrap(True)
        layout.addWidget(label)

        self._log_view = QPlainTextEdit()
        self._log_view.setReadOnly(True)
        self._log_view.setMinimumHeight(160)
        layout.addWidget(self._log_view)

        button_row = QHBoxLayout()
        button_row.setSpacing(8)

        self._log_button = QPushButton("Emit sample log entry")
        self._log_button.setObjectName("AccentButton")
        self._log_button.clicked.connect(self._emit_log_entry)
        button_row.addWidget(self._log_button)
        button_row.addStretch(1)

        layout.addLayout(button_row)
        return group

    # ------------------------------------------------------------------
    # Slots and callbacks
    # ------------------------------------------------------------------
    def _connect_signals(self) -> None:
        self._data.dataChanged.connect(self._on_data_changed)
        self._data.messageBroadcast.connect(self._on_message_broadcast)
        self._data.configUpdated.connect(self._on_config_updated)
        self._logger.signal.connect(self._append_log)
        self._data_input.textChanged.connect(self._update_shared_value)

    def _update_shared_value(self, value: str) -> None:
        self._data.set_data("demo.text", value)

    def _on_data_changed(self, key: str, value: object) -> None:
        if key == "demo.text":
            display = value if value else "<empty>"
            self._data_echo.setText(f"Shared value: {display}")

    def _broadcast_message(self) -> None:
        payload = self._data_input.text().strip() or "(no payload)"
        self._data.broadcast_message("demo.broadcast", payload)

    def _on_config_updated(self, payload: dict) -> None:
        summary = ', '.join(f"{k}={v}" for k, v in payload.items() if v is not None)
        self._log_view.appendPlainText(f"[CONFIG] {summary}")

    def _on_message_broadcast(self, channel: str, payload: object) -> None:
        if channel == "demo.broadcast":
            self._message_label.setText(f"Last broadcast: {payload}")

    def _emit_log_entry(self) -> None:
        accent = self._style.get_colour("accent")
        theme = self._config.get_value("theme").value  # type: ignore[union-attr]
        self._logger.info("Sample log using accent %s on %s theme", accent, theme)

    @Slot(str, str, str, str)
    def _append_log(self, timestamp: str, message: str, level: str, colour: str) -> None:
        text = f"[{timestamp}] {level:<8} {message}"
        self._log_view.appendPlainText(text)

    def _cycle_accent_colour(self) -> None:
        setting = self._config.get_value("accent")  # type: ignore[assignment]
        current = setting.value
        palette = setting.values or [current]
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
        current = str(setting.value).lower()
        new_value = "dark" if current == "light" else "light"
        self._config.set_value("theme", new_value)
        setting.value = new_value
        self._logger.info("Theme toggled to %s mode", new_value)
        self._apply_style_updates()

    # ------------------------------------------------------------------
    # Styling helpers
    # ------------------------------------------------------------------
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
            qss_path = getattr(qss_setting, 'value', qss_setting)
        except Exception:
            qss_path = None
        self._data.update_config({
            'accent': accent,
            'support': support,
            'neutral': neutral,
            'theme': str(theme),
            'qss_path': qss_path,
        })

        self._refresh_palette_swatches()
        self._populate_icon_list()
        self._update_theme_button_text()

    def _refresh_palette_swatches(self) -> None:
        accent_hex = self._style.get_colour("accent")
        support_hex = self._style.get_colour("support")
        neutral_hex = self._style.get_colour("neutral")

        self._accent_label.setStyleSheet(self._colour_chip_stylesheet(accent_hex))
        self._accent_label.setText(f"Accent\n{accent_hex}")
        self._support_label.setStyleSheet(self._colour_chip_stylesheet(support_hex))
        self._support_label.setText(f"Support\n{support_hex}")
        self._neutral_label.setStyleSheet(self._colour_chip_stylesheet(neutral_hex))
        self._neutral_label.setText(f"Neutral\n{neutral_hex}")

    def _populate_icon_list(self) -> None:
        accent_hex = self._style.get_colour("accent")
        support_hex = self._style.get_colour("support")
        theme = str(self._config.get_value("theme").value).lower()  # type: ignore[union-attr]
        tint = support_hex if theme == "dark" else accent_hex

        self._icon_list.clear()
        available = self._icons.list_icons()
        for base_name in self._ICON_NAMES:
            resolved = self._icons.search_icons(base_name, available)
            if not resolved:
                continue
            name = resolved[0]
            pixmap = self._icons.get_pixmap(name, tint, 48)
            if pixmap and not pixmap.isNull():
                item = QListWidgetItem(QIcon(pixmap), name)
                self._icon_list.addItem(item)

    def _update_theme_button_text(self) -> None:
        theme = str(self._config.get_value("theme").value).lower()  # type: ignore[union-attr]
        target = "dark" if theme == "light" else "light"
        self._theme_button.setText(f"Switch to {target.capitalize()} theme")

    # ------------------------------------------------------------------
    # Utility helpers
    # ------------------------------------------------------------------
    def _build_colour_label(self, title: str, key: str) -> QLabel:
        label = QLabel(f"{title}\n<unknown>")
        label.setAlignment(Qt.AlignCenter)
        label.setMinimumSize(120, 60)
        label.setObjectName(f"ColourChip_{key}")
        return label

    @staticmethod
    def _colour_chip_stylesheet(colour: str) -> str:
        return (
            "border-radius: 6px;"
            "padding: 6px;"
            "color: white;"
            "font-weight: bold;"
            f"background-color: {colour};"
        )

    def _window_title(self) -> str:
        try:
            app_name = self._config.get_value("name")
        except Exception:
            app_name = "QtPop Showcase"
        return str(getattr(app_name, "value", app_name))

    def closeEvent(self, event) -> None:  # type: ignore[override]
        self._qss.clear_temp_svgs()
        super().closeEvent(event)


def main() -> int:
    """Entry point for manual execution."""
    app = QApplication(sys.argv)
    config_path = Path(__file__).resolve().parent / "config" / "demo_config.json"
    qtpop = QtPop.instance().initialise(config_path)

    window = DemoWindow(qtpop, config_path)
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
