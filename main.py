import logging
import sys
from pathlib import Path

import nova.app
from nova.core.context import NovaContext
from nova.core.config import ConfigManager
from nova.core.style import StyleManager
from nova.core.icons import IconManager

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)

if __name__ == "__main__":
    root_dir = Path(__file__).parent

    # Initialize Core Managers
    print("Initializing Nova Core Managers...")
    config = ConfigManager(root_dir / "config" / "config.json")

    style = StyleManager()
    accent = config.get_value("appearance.accent", "#0088CC")
    theme  = config.get_value("appearance.theme",  "dark")
    style.initialise(accent_hex=accent, theme=theme)

    icons = IconManager()  # inline-only; no path argument needed

    # Create Context
    ctx = NovaContext(config, style, icons)

    logging.info("Nova initialized successfully.")

    try:
        nova.app.run(ctx)
    except Exception as e:
        logging.critical("Unhandled exception: %s", e, exc_info=True)
        sys.exit(1)
