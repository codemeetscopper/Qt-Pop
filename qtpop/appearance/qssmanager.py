import logging
import re
import time
import uuid
from pathlib import Path


class QSSManager:
    """
    Convert custom QSS tokens into standard QSS.

    - Replaces image tokens: <image: icon name; color:accent_l1>
      -> generates a temp colorized SVG and returns url('file://...').
    - Replaces color tokens: <accent>, <accent_l1>, <bg>, <fg1>, etc.
    """

    _styler = None
    _icon_manager = None
    _log = None
    _image_token_re = re.compile(r"<img:\s*(.+?);\s*color:(.+?)>", flags=re.IGNORECASE)
    _colour_token_re = re.compile(r"<\s*([a-zA-Z0-9_]+)\s*>")

    def __init__(self, icon_manager, style_manager, logger):
        self._icon_manager = icon_manager
        self._styler = style_manager
        self._logger = logger


    @classmethod
    def process(cls, raw_qss: str) -> str:
        # First replace image tokens
        def image_replacer(m):
            inner = m.group(1).strip()
            parts = [p.strip() for p in inner.split(';') if p.strip()]
            if not parts:
                return m.group(0)

            name_part = parts[0].strip().strip('\'"')
            colour_part = None
            for p in parts[1:]:
                if ':' in p:
                    k, v = p.split(':', 1)
                    if k.strip().lower() == 'color':
                        colour_part = v.strip()

            # resolve colour
            resolved_colour = None
            try:
                if colour_part:
                    # allow direct key like accent_l1 or token form <accent_l1>
                    key_m = re.match(r"^<\s*([a-zA-Z0-9_]+)\s*>$", colour_part)
                    if key_m:
                        key = key_m.group(1)
                        resolved_colour = cls._styler.get_colour(key)
                    elif colour_part.startswith('#'):
                        resolved_colour = colour_part
                    else:
                        resolved_colour = cls._styler.get_colour(colour_part)
                else:
                    resolved_colour = cls._styler.get_colour('accent')
            except Exception:
                cls._log.debug("Failed to resolve colour '%s', defaulting to #000000", colour_part)
                resolved_colour = "#000000"

            try:
                # try direct fetch first
                svg_data = None
                try:
                    svg_data = cls._icon_manager.get_svg_data(name_part)
                except Exception:
                    svg_data = None

                # fallback to search
                if not svg_data:
                    all_icons = cls._icon_manager.list_icons()
                    candidates = cls._icon_manager.search_icons(name_part, all_icons)
                    if not candidates:
                        cls._log.warning("Icon '%s' not found", name_part)
                        return m.group(0)
                    icon_name = candidates[0]
                    try:
                        svg_data = cls._icon_manager.get_svg_data(icon_name)
                    except Exception:
                        svg_data = None

                if not svg_data:
                    cls._log.warning("Icon '%s' missing svg data", name_part)
                    return m.group(0)

                # inject colour style into svg content
                style_snip = f"<style> *{{fill:{resolved_colour} !important; stroke:{resolved_colour} !important}} </style>"
                new_content, n = re.subn(r"(<svg[^>]*>)", lambda mm: mm.group(0) + style_snip, svg_data, count=1,
                                         flags=re.IGNORECASE)
                if n == 0:
                    new_content = f"<svg>{style_snip}</svg>\n" + svg_data

                content = cls.make_qt_svg_temp(new_content)
                return content
            except Exception as e:
                cls._log.exception("Failed to process image token: %s", e)
                return m.group(0)

        intermediate = cls._image_token_re.sub(image_replacer, raw_qss)

        # Then replace colours
        def colour_replacer(m):
            key = m.group(1)
            try:
                return cls._styler.get_colour(key)
            except Exception:
                try:
                    # fallback to StyleManager static access if AppCntxt not ready
                    return cls._styler.get_colour(key)
                except Exception:
                    cls._log.warning("Unknown colour key: %s", key)
                    return "#000000"

        processed = cls._colour_token_re.sub(colour_replacer, intermediate)
        return processed

    @classmethod
    def make_qt_svg_temp(cls, svg_content: str, delay_delete: float = 1.0) -> str:
        """
        Creates a temporary SVG file in the current working directory (or a 'tmp_qss_icons' folder),
        returns a Qt-compatible URL (url('path/to/file.svg')),
        and schedules the file for deletion after a short delay.

        Args:
            svg_content (str): The SVG content to write.
            delay_delete (float): How many seconds to wait before deleting the file (default 1.0).

        Returns:
            str: A Qt-compatible URL string, e.g. url('C:/path/file.svg')
        """
        # Create a stable temp directory within the project
        temp_dir = Path.cwd() / "tmp_qss_icons"
        temp_dir.mkdir(exist_ok=True)

        # Generate a unique filename
        temp_file = temp_dir / f"icon_{uuid.uuid4().hex}.svg"

        # Write the SVG content
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(svg_content)

        # Convert to Qt-compatible path (forward slashes)
        qt_path = temp_file.resolve().as_posix()

        # Schedule deletion in the background after delay
        # (so Qt has time to read the file)
        import threading
        def delete_later(path: Path):
            time.sleep(delay_delete)
            try:
                if path.exists():
                    path.unlink()
            except Exception as e:
                print(f"[make_qt_svg_temp] Failed to delete {path}: {e}")

        threading.Thread(target=delete_later, args=(temp_file,), daemon=True).start()

        return f"url('{qt_path}')"