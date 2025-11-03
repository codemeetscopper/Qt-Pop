from PySide6.QtGui import QFontDatabase, QFont
import os
from itertools import cycle

from qtpop.qtpoplogger import debug_log

@debug_log
class FontManager:
    _instance = None

    def __init__(self):
        self._family_cycle = None
        self._loaded_families = []  # List of loaded font families
        self._font_map = {}  # Maps tags like 'h1' to font info

    def _init(self):
        self._family_cycle = None     # Iterator for round-robin font assignment

    @debug_log
    def load_font(self, font_path: str, tag: str = None, size: int = None):
        """
        Loads a TTF font and optionally maps it to a tag with a size.
        If tag/size is not provided, font is added to the pool for round-robin mapping.
        """
        if not os.path.exists(font_path):
            raise FileNotFoundError(f"Font file not found: {font_path}")

        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id == -1:
            raise RuntimeError(f"Failed to load font: {font_path}")

        families = QFontDatabase.applicationFontFamilies(font_id)
        if not families:
            raise RuntimeError(f"No font families found in: {font_path}")

        family = families[0]
        self._loaded_families.append(family)
        self._family_cycle = cycle(self._loaded_families)

        if tag:
            self._font_map[tag] = {
                'family': family,
                'size': size if size else 12  # Default size
            }

    @debug_log
    def set_font_size(self, tag: str, size: int):
        """Sets the size for a given font tag."""
        if tag in self._font_map:
            self._font_map[tag]['size'] = size
        else:
            raise KeyError(f"Font tag '{tag}' not found.")

    @debug_log
    def get_font(self, tag: str, size: int = 12) -> QFont:
        """
        Returns a QFont object for the given tag.
        If tag is not mapped, assigns a font from the pool.
        """
        if tag not in self._font_map:
            # Assign a font from the pool if available
            if not self._loaded_families:
                raise RuntimeError("No fonts loaded to assign.")

            family = next(self._family_cycle)
            self._font_map[tag] = {
                'family': family,
                'size': size  # Default size
            }

        font_info = self._font_map[tag]
        return QFont(font_info['family'], font_info['size'])

    @debug_log
    def get_font_map(self):
        return self._font_map
