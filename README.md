# Qt-Pop
modern, modular Qt styling library for desktop applications. qt-pop provides fonts, icons, themes, and UI utilities to make your PyQt/PySide apps look polished, consistent, and ready for production. Customize colors, switch themes, and integrate sleek icons—all with minimal effort.

## Demo application

A comprehensive QtPop showcase lives in `demo_app/`. It wires together the
configuration parser, font loader, icon utilities, live QSS token processing,
and the shared data/logger signals. Launch it with:

```bash
python -m demo_app.main
```

The demo expects PySide6 to be installed and will automatically load the sample
configuration in `demo_app/config/demo_config.json`.
