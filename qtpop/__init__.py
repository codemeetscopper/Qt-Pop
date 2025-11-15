"""Public entry-point for QtPop, a PySide6 style wrapper."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Iterable

from qtpop.appearance.fontmanager import FontManager
from qtpop.appearance.iconmanager import IconManager
from qtpop.appearance.qssmanager import QSSManager
from qtpop.appearance.stylemanager import StyleManager
from qtpop.configuration.parser import ConfigurationManager
from qtpop.qtpopdatalayer import QtPopDataLayer
from qtpop.qtpoplogger import QtPopLogger, qt_logger

__all__ = [
    "QtPop",
    "FontManager",
    "IconManager",
    "QSSManager",
    "StyleManager",
    "ConfigurationManager",
    "QtPopDataLayer",
    "QtPopLogger",
    "qt_logger",
]


class QtPop:
    """High-level facade that wires QtPop managers together."""

    _instance: "QtPop" | None = None

    def __init__(self) -> None:
        self.__class__._instance = self

        self._initialized = False
        self._config_path: Path | None = None

        self.config: ConfigurationManager | None = None
        self.font: FontManager | None = None
        self.style = StyleManager
        self.icon: IconManager | None = None
        self.qss: QSSManager | None = None
        self.log: QtPopLogger | None = None
        self.data: QtPopDataLayer | None = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    def initialise(self, config_path: str | os.PathLike[str]) -> "QtPop":
        """Bootstrap QtPop using the provided configuration JSON."""
        resolved_config = Path(config_path).expanduser().resolve()
        if not resolved_config.is_file():
            raise FileNotFoundError(f"Configuration file not found: {resolved_config}")

        if self._initialized and resolved_config == self._config_path:
            return self

        self._config_path = resolved_config
        self.log = qt_logger
        self.log.info(f"Initialising QtPop with configuration: {resolved_config}")

        # Core managers
        self.data = QtPopDataLayer.instance()
        self.config = ConfigurationManager(json_path=str(resolved_config))
        self.font = FontManager()
        self.icon = IconManager()
        self.style = StyleManager

        # Load resources declared in configuration
        self._configure_icons()
        self._configure_fonts()
        self._configure_style()

        # Build QSS manager and apply styling immediately
        self.qss = QSSManager(self.icon, self.style, self.log)
        self._apply_qss()

        self._initialized = True
        return self

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def is_initialized(self) -> bool:
        return self._initialized

    @classmethod
    def instance(cls) -> "QtPop":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get_instance(self) -> "QtPop":
        return self.__class__.instance()

    # ------------------------------------------------------------------
    # Configuration helpers
    # ------------------------------------------------------------------
    def _configure_icons(self) -> None:
        icons_setting = self._setting_value("icon_path")
        icons_path = self._resolve_path(icons_setting)
        if not icons_path:
            return
        if not icons_path.exists():
            self.log.warning("Icon path does not exist: %s", icons_path)
            return
        self.icon.set_images_path(str(icons_path))

    def _configure_fonts(self) -> None:
        fonts_setting = self._setting_value("font_path")
        fonts_path = self._resolve_path(fonts_setting)
        if not fonts_path or not fonts_path.exists():
            if fonts_setting:
                self.log.warning("Font path does not exist: %s", fonts_path)
            return

        font_files = list(self._iter_font_files(fonts_path))
        if not font_files:
            self.log.info("No font files discovered in %s", fonts_path)
            return

        for font_file in font_files:
            try:
                self.font.load_font(str(font_file))
            except Exception as exc:  # pragma: no cover - depends on font availability
                self.log.warning("Failed to load font %s: %s", font_file, exc)

    def _configure_style(self) -> None:
        accent = str(self._setting_value("accent") or "#3f51b5")
        support = str(self._setting_value("support") or "#ff9800")
        neutral = str(self._setting_value("neutral") or "#607d8b")
        theme = str(self._setting_value("theme") or "light").lower()
        if theme not in {"light", "dark"}:
            self.log.warning("Unknown theme '%s', defaulting to 'light'", theme)
            theme = "light"

        initialised = self.style.initialise(accent, support, neutral, theme)
        if not initialised:
            raise RuntimeError("Failed to initialise StyleManager with configuration colours.")

    def _apply_qss(self) -> None:
        qss_setting = self._setting_value("qss_path")
        qss_path = self._resolve_path(qss_setting)
        stylesheet = ""

        if qss_path and qss_path.is_file():
            stylesheet = qss_path.read_text(encoding="utf-8")
        else:
            default_qss = self._default_qss_path()
            if default_qss.is_file():
                stylesheet = default_qss.read_text(encoding="utf-8")
            elif qss_setting:
                self.log.warning("QSS file not found: %s", qss_path or qss_setting)

        self.qss.set_style(stylesheet)

    # ------------------------------------------------------------------
    # Utility helpers
    # ------------------------------------------------------------------
    def _setting_value(self, key: str):
        if not self.config:
            return None
        try:
            setting = self.config.get_value(key)
        except Exception:
            return None
        return getattr(setting, "value", setting)

    def _resolve_path(self, value) -> Path | None:
        if value in (None, ""):
            return None
        text = str(value)
        if re.match(r"^[a-zA-Z]:[\\/].*", text):
            return Path(text)
        candidate = Path(text).expanduser()
        if candidate.is_absolute():
            return candidate
        if not self._config_path:
            return candidate.resolve()
        return (self._config_path.parent / candidate).resolve()

    @staticmethod
    def _iter_font_files(directory: Path) -> Iterable[Path]:
        for pattern in ("*.ttf", "*.otf"):  # extendable
            yield from directory.glob(pattern)

    @staticmethod
    def _default_qss_path() -> Path:
        return Path(__file__).resolve().parent.parent / "resources" / "qss" / "default.qss"
