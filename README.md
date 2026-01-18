# Qt-Pop

Qt-Pop is a modern, modular styling toolkit for PySide6/PyQt desktop applications. It provides a cohesive theme system (colors, palettes, QSS processing), icon rendering utilities, font management, configuration handling, and centralized logging/data signals to keep your UI consistent and maintainable.

## Goals

* **Consistency**: Centralize themes, fonts, icons, and QSS token resolution so the UI looks uniform across the app.
* **Configurability**: Load user and static settings from JSON and persist them via `QSettings`.
* **Ergonomics**: Provide simple APIs for loading fonts, retrieving icons, applying palettes, and updating styles.

## Architecture Overview

Qt-Pop is composed of small, focused managers coordinated by the `QtPop` facade class.

### High-Level Flow

1. **`QtPop.initialise(config_path)`** reads configuration values.
2. **Style, icon, and font managers** are created and configured.
3. **`QSSManager`** resolves tokens and applies the palette + stylesheet to the running `QApplication`.
4. **`QtPopDataLayer`** provides cross-component signals for data, theme, and configuration updates.

### Core Components

| Component | Responsibility | Key Files |
| --- | --- | --- |
| `QtPop` | Facade for initialization and manager wiring. | `qtpop/__init__.py` |
| `ConfigurationManager` | Load configuration JSON, expose settings, and sync with `QSettings`. | `qtpop/configuration/parser.py` |
| `StyleManager` | Generate color tiers and `QPalette` from accent/support/neutral colors. | `qtpop/appearance/stylemanager.py` |
| `IconManager` | Search, cache, and render SVG icons as `QPixmap`/`QImage` (sync or async). | `qtpop/appearance/iconmanager.py` |
| `QSSManager` | Replace color and image tokens in QSS and apply the stylesheet. | `qtpop/appearance/qssmanager.py` |
| `FontManager` | Load TTF fonts and map them to tags/sizes. | `qtpop/appearance/fontmanager.py` |
| `QtPopLogger` | Colored console logging + Qt signal emission. | `qtpop/qtpoplogger.py` |
| `QtPopDataLayer` | Singleton data bus with Qt signals for inter-UI updates. | `qtpop/qtpopdatalayer.py` |

### Folder Structure (Key Areas)

```
qtpop/
  appearance/          # Styles, icons, fonts, QSS processing
  configuration/       # Config models, parsing, and validation
  qtpoplogger.py        # Logging utilities
  qtpopdatalayer.py     # Signal-based data layer
app/                    # Demo application showcasing Qt-Pop usage
config/                 # Example configuration JSON
resources/              # Fonts, icons, QSS (referenced by config)
```

## Usage

### Installation

Qt-Pop is currently a local library. Install dependencies (e.g., PySide6) and add the repository to your Python path.

```bash
pip install PySide6 colorama
```

### Initialization

Create a `QtPop` instance and initialize it with a configuration file.

```python
from qtpop import QtPop

qt_pop = QtPop().initialise("config/config.json")
qt_pop.log.info("QtPop initialized")
```

The configuration file drives your theme, icons, and other settings. For example, the demo config includes `accent`, `support`, `neutral`, and `theme` values, plus icon and font paths.

### Applying QSS with Tokens

`QSSManager` allows your stylesheet to use semantic color and image tokens that are resolved at runtime.

```qss
QWidget {
    background: <bg>;
    color: <fg>;
}

QPushButton {
    background: <accent>;
}

QToolButton {
    image: <img: settings; color: accent_l1>;
}
```

Token rules:

* **Color tokens**: `<accent>`, `<accent_l1>`, `<bg>`, `<fg2>`, etc.
* **Image tokens**: `<img: icon_name; color: accent>` uses the `IconManager` to colorize SVG icons.

### Working With Managers

**Fonts**

```python
qt_pop.font.load_font("resources/fonts/Inter-Regular.ttf", tag="body", size=12)
body_font = qt_pop.font.get_font("body")
```

**Icons (sync)**

```python
pixmap = qt_pop.icon.get_pixmap("settings", color="#55aa7f", size=24)
```

**Icons (async)**

```python
qt_pop.icon.get_pixmap("settings", color="#55aa7f", size=24, async_load=True)
qt_pop.icon._notifier.icon_loaded.connect(lambda name, image: print("Loaded", name))
```

**Styles**

```python
accent = qt_pop.config.get_value("accent").value
qt_pop.style.initialise(accent_hex=accent, support_hex="#FF9800", neutral_hex="#4CAF50", theme="light")
palette = qt_pop.style.get_palette()
```

### Configuration Access

```python
accent_setting = qt_pop.config.get_value("accent")
qt_pop.config.set_value("theme", "dark")
```

### Demo Application

The `app/` directory includes a sample PySide6 application that demonstrates Qt-Pop usage. The entry point is `main.py`.

## Advantages

* **Single Source of Truth**: Centralized theme + palette logic avoids color drift and manual duplication.
* **Flexible Icon Rendering**: Colorized SVGs with caching and async loading for better performance.
* **QSS Tokenization**: Author QSS in semantic terms (`<accent>`, `<bg>`) rather than hard-coded hex values.
* **Expandable Configuration**: Built-in support for user/static settings and persistence via `QSettings`.
* **UI Communication**: Signal-based data layer makes it easier to propagate state changes across widgets.

## Typical Workflow

1. Define your theme settings in `config/config.json`.
2. Initialize `QtPop` at application startup.
3. Use `QSSManager.set_style()` to apply your QSS with tokens.
4. Fetch icons/fonts as needed via the manager APIs.

## Notes & Considerations

* `QSSManager` writes temporary SVGs to a `tmp_qss_icons/` directory and deletes them shortly after use.
* The configuration uses a JSON structure with `user` and `static` settings that get mirrored into `QSettings`.
* Theme variants (`_l1`, `_l2`, `_d1`, etc.) are generated automatically based on the theme mode.

## License

See [LICENSE](LICENSE).
