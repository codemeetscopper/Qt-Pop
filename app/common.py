import re

ansi_regex = re.compile(r'\x1b\[(?:38;5;(\d{1,3})|9[0-7]|3[0-7]|0)m')

def ansi_to_hex(match):
    """Convert ANSI escape match to hex color."""
    code = match.group(1)
    if code is not None:
        # 256-color mode
        code = int(code)
        return ansi256_to_hex(code)
    else:
        # 16-color / classic ANSI
        ansi_code = match.group(0)
        return ansi16_to_hex(ansi_code)


def ansi16_to_hex(code):
    """16-color ANSI mapping"""
    mapping = {
        "\x1b[30m": "#000000",
        "\x1b[31m": "#FF0000",
        "\x1b[32m": "#00FF00",
        "\x1b[33m": "#FFFF00",
        "\x1b[34m": "#0000FF",
        "\x1b[35m": "#FF00FF",
        "\x1b[36m": "#00FFFF",
        "\x1b[37m": "#FFFFFF",
        "\x1b[90m": "#808080",
        "\x1b[91m": "#FF5555",
        "\x1b[92m": "#55FF55",
        "\x1b[93m": "#FFFF55",
        "\x1b[94m": "#5555FF",
        "\x1b[95m": "#FF55FF",
        "\x1b[96m": "#55FFFF",
        "\x1b[97m": "#FFFFFF",
        "\x1b[0m": "#FFFFFF",  # reset
    }
    return mapping.get(code, "#FFFFFF")


def ansi256_to_hex(code: int) -> str | None:
    """Convert 256-color ANSI code (0-255) to hex string."""
    if code < 16:
        # standard colors
        standard = [
            0x000000, 0x800000, 0x008000, 0x808000, 0x000080, 0x800080, 0x008080, 0xc0c0c0,
            0x808080, 0xff0000, 0x00ff00, 0xffff00, 0x0000ff, 0xff00ff, 0x00ffff, 0xffffff
        ]
        return f"#{standard[code]:06X}"
    elif 16 <= code <= 231:
        code -= 16
        r = (code // 36) * 51
        g = ((code % 36) // 6) * 51
        b = (code % 6) * 51
        return f"#{r:02X}{g:02X}{b:02X}"
    elif 232 <= code <= 255:
        gray = (code - 232) * 10 + 8
        return f"#{gray:02X}{gray:02X}{gray:02X}"
    return None


def strip_ansi_codes(text):
    """Remove ANSI codes but keep the color info for HTML."""
    return ansi_regex.sub("", text)