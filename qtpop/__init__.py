import os

from qtpop.appearance.fontmanager import FontManager
from qtpop.appearance.iconmanager import IconManager
from qtpop.appearance.qssmanager import QSSManager
from qtpop.appearance.stylemanager import StyleManager
from qtpop.configuration.parser import ConfigurationManager
from qtpop.qtpopdatalayer import QtPopDataLayer
from qtpop.qtpoplogger import QtPopLogger, debug_log, qt_logger


@debug_log
class QtPop:
    _instance = None
    _initialized = False
    _config_path = ""

    def __init__(self):
        self.config: ConfigurationManager = None
        self.font: FontManager = None
        self.style: StyleManager = None
        self.icon: IconManager = None
        self.qss: QSSManager = None
        self.log: QtPopLogger = None
        self.data: QtPopDataLayer = None

    @debug_log
    def initialise(self, config_path: str):
        self._config_path = config_path
        if self._initialized:
            return self

        # Initialize all managers
        self.log = qt_logger
        self.data = QtPopDataLayer().instance()
        self.config = ConfigurationManager(json_path=config_path)

        self.font = FontManager()

        icons_path = self.config.get_value('icon_path')
        self.icon = IconManager()
        self.icon.set_images_path(icons_path)

        accent = self.config.get_value('accent')
        support = self.config.get_value('support')
        neutral = self.config.get_value('neutral')
        theme = self.config.get_value('theme')
        self.style = StyleManager()
        self.style.initialise(accent, support, neutral, theme)

        self.qss = QSSManager(self.icon, self.style, self.log)
        self._initialized = True
        return self

    def is_initialized(self):
        return self._initialized

    def get_instance(self):
        return self.__class__._instance
