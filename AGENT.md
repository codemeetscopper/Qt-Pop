# Qt-Pop — AI Agent Context File

This file provides structured context for AI coding agents working on the Qt-Pop project.

---

## Project Overview

**Qt-Pop** is a modular styling and theming toolkit for PySide6 desktop applications.
It is designed to be embedded into any PySide6 app as a library (`qtpop/`) that provides:

- Centralized color palette generation (light/dark themes, sRGB blending)
- Token-based QSS stylesheet processing (`<accent>`, `<img: name; color: key>`)
- Async/sync SVG icon loading with per-color caching
- Font loading and tag-based mapping
- JSON + QSettings configuration management
- Colored console logging with Qt signal emission for UI integration
- Thread-safe singleton data bus for inter-widget communication

The `app/` directory is a demo application that exercises the toolkit.

---

## Directory Layout

```
Qt-Pop/
├── qtpop/                        # Core library — import this in your app
│   ├── __init__.py               # QtPop facade — single entry point
│   ├── qtpoplogger.py            # Logging: QtPopLogger, qt_logger, debug_log decorator
│   ├── qtpopdatalayer.py         # Singleton data bus (Qt signals)
│   ├── appearance/
│   │   ├── stylemanager.py       # Color palette generation (class-level state)
│   │   ├── iconmanager.py        # SVG icon loader/cache (class-level state)
│   │   ├── qssmanager.py         # QSS token processor (class-level state)
│   │   └── fontmanager.py        # Font loader and tag-mapper (instance state)
│   └── configuration/
│       ├── parser.py             # ConfigurationManager — singleton, JSON + QSettings
│       ├── models.py             # Dataclasses: AppSettings, Configuration, SettingItem, PageMapping
│       └── exceptions.py         # Custom exceptions hierarchy
├── app/                          # Demo application (not part of the library)
│   ├── app.py                    # run(qt_pop) — creates QApplication, shows MainWindow
│   ├── mainwindow/               # Main window (UI + generated code)
│   └── widgets/                  # Custom demo widgets
├── config/
│   └── config.json               # Default configuration (relative paths only)
├── resources/
│   ├── fonts/                    # TTF font files
│   ├── images/                   # SVG icon files (Material Icons)
│   └── qss/                      # QSS stylesheet files with custom tokens
├── main.py                       # App launcher — resolves config path dynamically
├── requirements.txt              # pip dependencies
└── AGENT.md                      # This file
```

---

## Architecture Patterns

### Manager Design
All four appearance managers (`StyleManager`, `IconManager`, `QSSManager`, `FontManager`) use
**class-level (static) state** — meaning they are effectively singletons without explicit
`__new__` guards. Call their `@classmethod` methods directly on the class.
`ConfigurationManager` and `QtPopDataLayer` use explicit `__new__`-based singletons.

### Initialization Order (enforced by QtPop.initialise)
```
ConfigurationManager  →  FontManager  →  IconManager  →  StyleManager  →  QSSManager
```
`QSSManager` depends on `IconManager` and `StyleManager` being ready.

### Token Syntax in QSS Files
- Color token: `<accent>`, `<bg>`, `<fg1>`, `<accent_l2>`, etc.
- Image token: `<img: icon_name; color: accent_l1>`

All tokens are replaced by `QSSManager.process(raw_qss)` before the stylesheet is applied.

---

## Public API Reference

### QtPop (qtpop/__init__.py)
The main facade. Always initialize before use.
```python
qt_pop = QtPop()
qt_pop.initialise("/path/to/config.json")

qt_pop.log      # QtPopLogger
qt_pop.data     # QtPopDataLayer
qt_pop.config   # ConfigurationManager
qt_pop.font     # FontManager
qt_pop.icon     # IconManager
qt_pop.style    # StyleManager
qt_pop.qss      # QSSManager
```

### StyleManager (qtpop/appearance/stylemanager.py)
```python
StyleManager.initialise(accent_hex, support_hex, neutral_hex, theme)  # -> bool
StyleManager.get_colour("accent_l1")          # -> "#RRGGBB"
StyleManager.get_colour("bg", to_str=False)   # -> QColor
StyleManager.get_palette()                     # -> QPalette
StyleManager.mode()                            # -> "light" | "dark"
StyleManager.colour_map()                      # -> Dict[str, QColor]
StyleManager.is_initialised()                  # -> bool
```
Generated color keys: `bg`, `bg1`, `bg2`, `fg`, `fg1`, `fg2`,
`accent`, `accent_l1`..`accent_l3`, `accent_ln`, `accent_d1`..`accent_d3`, `accent_dn`,
and the same tiers for `support` and `neutral`.

### IconManager (qtpop/appearance/iconmanager.py)
```python
IconManager.set_images_path("resources/images/")
IconManager.list_icons()                                      # -> List[str]
IconManager.get_pixmap("home", "#FF0000", size=24)            # -> QPixmap | None
IconManager.get_pixmap("home", async_load=True)               # returns None, emits signal
IconManager.get_svg_data("home", "#FF0000", size=24)          # -> str (SVG text)
IconManager.search_icons("home", icon_list)                   # -> List[str]
IconManager.preload_common_icons(["home", "settings"])
IconManager.clear_cache()

# Connect to async results:
IconManager._notifier.icon_loaded.connect(lambda name, img: ...)
```

### QSSManager (qtpop/appearance/qssmanager.py)
```python
QSSManager(icon_manager, style_manager, logger)   # initializes class state
QSSManager.process(raw_qss_string)                # -> processed QSS string
QSSManager.set_style(raw_qss_string)              # processes and applies to QApplication
QSSManager.clear_temp_svgs()                      # cleans tmp_qss_icons/ directory
```

### ConfigurationManager (qtpop/configuration/parser.py)
```python
cfg = ConfigurationManager(json_path="config/config.json")
cfg.get_value("accent")                # -> SettingItem
cfg.get_value("accent").value          # -> "#55aa7f"
cfg.get_value("version", as_string=True)
cfg.set_value("accent", "#112233")
cfg.get_all_keys()                     # -> List[str]
cfg.save()                             # persists to JSON
```

### FontManager (qtpop/appearance/fontmanager.py)
```python
fm = FontManager()
fm.load_font("resources/fonts/Roboto.ttf", tag="body", size=12)
fm.load_font("resources/fonts/Inter.ttf")   # added to round-robin pool
fm.get_font("body")                          # -> QFont
fm.get_font("unknown_tag")                   # assigns from pool
fm.set_font_size("body", 14)
fm.get_font_map()                            # -> dict
```

### QtPopLogger (qtpop/qtpoplogger.py)
```python
from qtpop.qtpoplogger import qt_logger, debug_log

qt_logger.info("message")
qt_logger.warning("message")
qt_logger.error("message")
qt_logger.exception("message")
qt_logger.enable_debug(True)     # enables @debug_log decorator tracing

# Connect UI to log stream:
qt_logger.signal.connect(lambda ts, msg, level, color: ...)

# Decorator for function-call tracing (no-op when DEBUG_ENABLE=False):
@debug_log
def my_function(...): ...
```

### QtPopDataLayer (qtpop/qtpopdatalayer.py)
```python
data = QtPopDataLayer.instance()
data.set_data("key", value)           # emits dataChanged(key, value)
data.get_data("key", default=None)
data.broadcast_message("channel", payload)   # emits messageBroadcast
data.update_style("theme_key")        # emits styleUpdated
data.update_config(config_dict)       # emits configUpdated

# Signals:
data.dataChanged.connect(...)
data.styleUpdated.connect(...)
data.configUpdated.connect(...)
data.messageBroadcast.connect(...)
```

---

## Configuration Schema (config/config.json)

```json
{
  "configuration": {
    "user": {
      "<key>": {
        "name": "Display Name",
        "shortname": "<key>",
        "value": "<current value>",
        "values": ["<option1>", "<option2>"],
        "description": "...",
        "type": "colorpicker|dropdown|text|filebrowse|folderbrowse",
        "accessibility": "user",
        "group": "Group Name",
        "icon": "images/icon.svg"
      }
    },
    "static": {
      "<key>": "<value>"
    }
  },
  "page_mapping": {
    "defaults": {
      "<PageName>": {
        "widget_ref": "module.path.to.widget",
        "enabled": true,
        "index": 1,
        "icon": "images/icon.svg",
        "selectable": true,
        "license_required": false
      }
    },
    "plugins": {}
  }
}
```

**Important:** All paths in `config.json` must be relative (e.g., `resources/images/`).
The application resolves them relative to the working directory at runtime.

---

## Common Pitfalls

1. **`QSSManager` uses class-level `__init__`** — calling `QSSManager(icon, style, log)`
   initializes class state, not instance state. All subsequent calls use the class directly.

2. **`StyleManager` must be initialized before `QSSManager.process()`** is called.
   If `StyleManager.initialise()` returns `False`, check the logger for the error.

3. **`IconManager.get_pixmap()` with `async_load=True`** returns `None` immediately.
   Connect to `IconManager._notifier.icon_loaded` signal to receive the `QImage`.

4. **Config paths are relative** — loaded relative to `os.getcwd()`, which is typically
   the project root when running `main.py`.

5. **`@debug_log` is a no-op by default** — set `DEBUG_ENABLE = True` in `qtpoplogger.py`
   or call `qt_logger.enable_debug(True)` to activate function-call tracing.

6. **`tmp_qss_icons/`** — temp SVG files written by `QSSManager` for QSS image tokens.
   They are deleted after ~1 second. Call `QSSManager.clear_temp_svgs()` on shutdown.

---

## Adding a New Manager or Feature

1. Create the module under `qtpop/appearance/` or a new subpackage.
2. Follow the existing class-level state pattern (or instance pattern for `FontManager`-style).
3. Expose it as an attribute on `QtPop` in `qtpop/__init__.py`.
4. Initialize it inside `QtPop.initialise()` in the correct dependency order.
5. Document the public API in this file under the API Reference section.
