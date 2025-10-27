import app.app
from qtpop import QtPop

if __name__ == "__main__":
    configPath = r"D:\Development\Python\Qt-Pop\config\config.json"
    qt_pop = QtPop()
    if qt_pop:
        qt_pop.initialise(configPath)
        qt_pop.log.info("QtPop initialized successfully.")
        app.app.run(qt_pop)