from __future__ import annotations

import logging
from typing import Dict, Union, Optional

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

_log = logging.getLogger(__name__)

ColourLike = Union[str, QColor]

class StyleManager:
    """
    Manages application theme colors.
    Replaces qtpop.appearance.stylemanager.StyleManager
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StyleManager, cls).__new__(cls)
            cls._instance._colours = {}
            cls._instance._palette = None
            cls._instance._resolved_mode = "light"
            cls._instance._font_family = '"Segoe UI", "Roboto", sans-serif'
        return cls._instance

    @classmethod
    def mode(cls) -> str:
        """Return the currently resolved theme mode ('dark' or 'light')."""
        return cls()._resolved_mode

    @classmethod
    def set_font_family(cls, family: str) -> None:
        """Store the custom font family so apply_theme() injects it into QSS."""
        cls()._font_family = f'"{family}", "Segoe UI", "Roboto", sans-serif'

    @classmethod
    def get_font_family(cls) -> str:
        return getattr(cls(), '_font_family', '"Segoe UI", "Roboto", sans-serif')

    @classmethod
    def initialise(cls, accent_hex: str, support_hex: str = "#FF9800", neutral_hex: str = "#4CAF50", theme: str = "dark"):
        inst = cls()
        try:
            accent = cls._to_qcolor(accent_hex)
            support = cls._to_qcolor(support_hex)
            neutral = cls._to_qcolor(neutral_hex)

            # Resolve "system" → detect OS colour scheme (Qt 6.5+)
            if theme == "system":
                try:
                    from PySide6.QtCore import Qt as _Qt
                    app = QApplication.instance()
                    if app is not None:
                        scheme = app.styleHints().colorScheme()
                        theme = "dark" if scheme == _Qt.ColorScheme.Dark else "light"
                    else:
                        theme = "dark"
                except Exception:
                    theme = "dark"

            inst._resolved_mode = theme

            white = QColor(255, 255, 255)
            black = QColor(0, 0, 0)
            
            # Simple blending helpers
            def blend(c1, c2, t):
                r = c1.red() * (1-t) + c2.red() * t
                g = c1.green() * (1-t) + c2.green() * t
                b = c1.blue() * (1-t) + c2.blue() * t
                return QColor(int(r), int(g), int(b))

            lighten = lambda c, t: blend(c, white, t)
            darken = lambda c, t: blend(c, black, t)

            def make_tiers(base, name):
                if theme == "light":
                    return {
                        f"{name}": base,
                        f"{name}_l1": lighten(base, 0.15),
                        f"{name}_l2": lighten(base, 0.30),
                        f"{name}_l3": lighten(base, 0.45),
                        f"{name}_ln": lighten(base, 0.90),
                        f"{name}_d1": darken(base, 0.15),
                        f"{name}_d2": darken(base, 0.30),
                    }
                else:
                    return {
                        f"{name}": base,
                        f"{name}_l1": darken(base, 0.15),
                        f"{name}_l2": darken(base, 0.30),
                        f"{name}_l3": darken(base, 0.45),
                        f"{name}_ln": darken(base, 0.90),
                        f"{name}_d1": lighten(base, 0.15),
                        f"{name}_d2": lighten(base, 0.30),
                    }

            inst._colours.update(make_tiers(accent, "accent"))
            inst._colours.update(make_tiers(support, "support"))
            inst._colours.update(make_tiers(neutral, "neutral"))

            if theme == "dark":
                bg = QColor(18, 18, 18)
                bg1 = lighten(bg, 0.05)
                bg2 = lighten(bg, 0.08)
                fg = QColor(255, 255, 255)
                fg1 = blend(fg, bg, 0.15) # slightly dimmed white
                fg2 = blend(fg, bg, 0.30)
            else:
                bg = QColor(247, 247, 247)
                bg1 = darken(bg, 0.05)
                bg2 = darken(bg, 0.08)
                fg = QColor(0, 0, 0)
                fg1 = blend(fg, bg, 0.15)
                fg2 = blend(fg, bg, 0.30)

            inst._colours.update({
                "bg": bg, "bg1": bg1, "bg2": bg2,
                "fg": fg, "fg1": fg1, "fg2": fg2
            })
            
            # Build palette (simplified)
            p = QPalette()
            p.setColor(QPalette.Window, bg)
            p.setColor(QPalette.WindowText, fg)
            p.setColor(QPalette.Base, bg)
            p.setColor(QPalette.AlternateBase, bg1)
            p.setColor(QPalette.Text, fg)
            p.setColor(QPalette.Button, bg1)
            p.setColor(QPalette.ButtonText, fg)
            p.setColor(QPalette.Highlight, accent)
            p.setColor(QPalette.HighlightedText, white)
            inst._palette = p

        except Exception as e:
            _log.error(f"StyleManager init failed: {e}")

    @classmethod
    def get_colour(cls, key: str) -> str:
        """Returns hex string for a color key."""
        inst = cls()
        key = key.lower()
        if key in inst._colours:
            c = inst._colours[key]
            return f"#{c.red():02X}{c.green():02X}{c.blue():02X}"
        return "#FF00FF" # Magenta fallback

    @classmethod
    def get_palette(cls) -> QPalette:
        return cls()._palette or QPalette()
        
    @classmethod
    def apply_theme(cls, app: QApplication, qss_content: str):
        """Process QSS and apply to app."""
        import re

        # Substitute font_family token first (not a colour)
        processed_qss = qss_content.replace("<font_family>", cls.get_font_family())

        # Replace colour tokens <token>
        def repl(m):
            key = m.group(1)
            return cls.get_colour(key)

        processed_qss = re.sub(r"<([a-zA-Z0-9_]+)>", repl, processed_qss)

        app.setPalette(cls.get_palette())
        app.setStyleSheet(processed_qss)

    @staticmethod
    def _to_qcolor(val: ColourLike) -> QColor:
        if isinstance(val, QColor): return val
        c = QColor(val)
        if not c.isValid(): raise ValueError(f"Invalid color: {val}")
        return c
