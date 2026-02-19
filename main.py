from pathlib import Path

import app.app
from qtpop import QtPop

if __name__ == "__main__":
    config_path = Path(__file__).parent / "config" / "config.json"
    qt_pop = QtPop()
    qt_pop.initialise(str(config_path))
    qt_pop.log.info("QtPop initialized successfully.")
    app.app.run(qt_pop)