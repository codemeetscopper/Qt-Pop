"""Utilities for parsing and applying Qt style sheets with QtPop tokens."""

from __future__ import annotations

import re
import threading
import time
import uuid
from pathlib import Path

from PySide6.QtWidgets import QApplication

from qtpop.appearance.iconmanager import IconManager
from qtpop.appearance.stylemanager import StyleManager
from qtpop.qtpoplogger import QtPopLogger, debug_log


class QSSManager:
    """Translate QtPop style tokens into valid Qt style sheets."""

    _image_token_re = re.compile(r"<img:\s*(.+?);\s*color:(.+?)>", flags=re.IGNORECASE)
    _colour_token_re = re.compile(r"<\s*([a-zA-Z0-9_]+)\s*>")

    def __init__(self, icon_manager: IconManager, style_manager: StyleManager, logger: QtPopLogger):
        self._icon_manager = icon_manager
        self._styler = style_manager
        self._log = logger
        self._style_sheet: str = ""

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    @debug_log
    def process(self, raw_qss: str) -> str:
        """Replace custom icon/colour tokens with Qt-friendly markup."""

        def replace_image(match: re.Match[str]) -> str:
            token = match.group(1).strip()
            pieces = [p.strip() for p in token.split(';') if p.strip()]
            if not pieces:
                return match.group(0)

            icon_name = pieces[0].strip().strip("'\"")
            colour_part = None
            for part in pieces[1:]:
                if ':' in part:
                    key, value = part.split(':', 1)
                    if key.strip().lower() == 'color':
                        colour_part = value.strip()
                        break

            resolved_colour = self._resolve_colour(colour_part)
            svg = self._resolve_icon(icon_name)
            if svg is None:
                return match.group(0)

            style_snip = (
                f"<style> *{{fill:{resolved_colour} !important; "
                f"stroke:{resolved_colour} !important}} </style>"
            )

            try:
                new_content, replaced = re.subn(
                    r"(<svg[^>]*>)",
                    lambda inner: inner.group(0) + style_snip,
                    svg,
                    count=1,
                    flags=re.IGNORECASE,
                )
            except re.error as ex:  # pragma: no cover - defensive
                self._log.warning("Failed to inject colour into svg %s: %s", icon_name, ex)
                new_content, replaced = svg, 0

            if replaced == 0:
                new_content = f"<svg>{style_snip}</svg>\n" + svg

            return self._make_qt_svg_temp(new_content)

        def replace_colour(match: re.Match[str]) -> str:
            key = match.group(1)
            colour = self._resolve_colour(key)
            return colour

        intermediate = self._image_token_re.sub(replace_image, raw_qss)
        return self._colour_token_re.sub(replace_colour, intermediate)

    @debug_log
    def set_style(self, style_sheet: str = "") -> None:
        """Apply the processed style to the running :class:`QApplication`."""
        if style_sheet:
            self._style_sheet = style_sheet

        if not self._style_sheet:
            processed = ""
        elif '<accent>' in self._style_sheet:
            processed = self.process(self._style_sheet)
        else:
            processed = self._style_sheet

        app = QApplication.instance()
        if not app:
            self._log.warning("No QApplication instance found to set style sheet.")
            return

        try:
            palette = self._styler.get_palette()
            app.setPalette(palette)
        except Exception as exc:  # pragma: no cover - palette should always be available
            self._log.warning("Failed to apply palette: %s", exc)

        app.setStyleSheet(processed)

    @debug_log
    def clear_temp_svgs(self) -> None:
        """Remove generated temporary icon files."""
        temp_dir = Path.cwd() / "tmp_qss_icons"
        if not temp_dir.exists():
            return

        for temp_file in temp_dir.glob("icon_*.svg"):
            try:
                temp_file.unlink()
            except Exception as exc:  # pragma: no cover - defensive
                self._log.warning("Failed to delete temp SVG file %s: %s", temp_file, exc)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _resolve_colour(self, colour_token: str | None) -> str:
        if not colour_token:
            key = 'accent'
        else:
            match = re.match(r"^<\s*([a-zA-Z0-9_]+)\s*>$", colour_token)
            key = match.group(1) if match else colour_token

        try:
            if key.startswith('#'):
                return key
            return self._styler.get_colour(key)
        except Exception:
            self._log.debug("Failed to resolve colour '%s', defaulting to #000000", colour_token)
            return "#000000"

    def _resolve_icon(self, name: str) -> str | None:
        try:
            svg_data = self._icon_manager.get_svg_data(name)
        except Exception:
            svg_data = None

        if svg_data:
            return svg_data

        try:
            icons = self._icon_manager.list_icons()
            candidates = self._icon_manager.search_icons(name, icons)
        except Exception:
            candidates = []

        if not candidates:
            self._log.warning("Icon '%s' not found", name)
            return None

        try:
            return self._icon_manager.get_svg_data(candidates[0])
        except Exception:
            self._log.warning("Icon '%s' missing svg data", name)
            return None

    @staticmethod
    def _make_qt_svg_temp(svg_content: str, delay_delete: float = 1.0) -> str:
        temp_dir = Path.cwd() / "tmp_qss_icons"
        temp_dir.mkdir(exist_ok=True)

        temp_file = temp_dir / f"icon_{uuid.uuid4().hex}.svg"
        temp_file.write_text(svg_content, encoding="utf-8")

        def delete_later(path: Path) -> None:
            time.sleep(delay_delete)
            try:
                if path.exists():
                    path.unlink()
            except Exception:  # pragma: no cover - best effort clean-up
                pass

        threading.Thread(target=delete_later, args=(temp_file,), daemon=True).start()
        return f"url('{temp_file.resolve().as_posix()}')"
