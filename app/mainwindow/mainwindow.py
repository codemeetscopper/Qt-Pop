from __future__ import annotations

import os

from PySide6.QtCore import QFile, Slot, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QGridLayout,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.mainwindow.ui_mainwindow import Ui_MainWindow
from app.widgets.addfontcard import AddFontCard
from app.widgets.colordisplaywidget import ColorDisplayWidget
from app.widgets.fontcard import FontCard
from app.widgets.homewidget import MinimalAIHome
from app.widgets.iconbrowser import IconBrowserWidget
from app.widgets.loggingwindow import QLogWidget
from app.widgets.settingsitemwidget import SettingItemWidget
from app.widgets.titlebar import CustomTitleBar
from qtpop import QtPop
from qtpop.configuration.models import SettingItem
from qtpop.qtpoplogger import debug_log


class MainWindow(QMainWindow):
    """Top-level window for the Qt-Pop demo application."""

    def __init__(self, qt_pop: QtPop):
        super().__init__()
        self.qt_pop = qt_pop

        self.titlebar: CustomTitleBar | None = None
        self.icon_widget: IconBrowserWidget | None = None
        self.home: MinimalAIHome | None = None
        self.log_widget: QLogWidget | None = None

        self._logging_initialised = False
        self._qss_initialised = False

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self._configure_window()
        self._load_custom_fonts()
        self._connect_core_signals()
        self.refresh_ui()

        self.qt_pop.log.info("MainWindow initialized successfully.")
        self.qt_pop.data.broadcast_message("main_window_opened", True)

    # ------------------------------------------------------------------
    # High-level orchestration
    # ------------------------------------------------------------------
    def _configure_window(self) -> None:
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)

    def _connect_core_signals(self) -> None:
        self.ui.saveBtn.clicked.connect(self.save_settings)
        self.ui.applybtn.clicked.connect(self.apply_qss_from_editor)
        self.ui.loadbtn.clicked.connect(self.load_qss_from_file)

    def _load_custom_fonts(self) -> None:
        self.qt_pop.font.load_font("resources/fonts/RobotoCondensed-VariableFont_wght.ttf", "h1", 18)
        self.qt_pop.font.load_font("resources/fonts/RobotoCondensed-VariableFont_wght.ttf", "h2", 14)
        self.qt_pop.font.load_font("resources/fonts/Roboto-VariableFont_wdth,wght.ttf", "p", 11)
        self.qt_pop.font.load_font("resources/fonts/RobotoCondensed-VariableFont_wght.ttf", "pc", 10)
        self.qt_pop.font.load_font("resources/fonts/Inconsolata-VariableFont_wdth,wght.ttf", "log", 11)
        self.qt_pop.font.load_font("resources/fonts/JollyLodger-Regular.ttf", "style", 12)

    @staticmethod
    def _setting_value(setting):
        return getattr(setting, "value", setting)

    @debug_log
    def refresh_ui(self) -> None:
        """Rebuild UI fragments that depend on runtime configuration."""
        self.setup_logging()
        self.setup_qss()
        self.apply_style()
        self.setup_palette()
        self.setup_settings()
        self.setup_fonts()
        self.setup_home()
        self.setup_icons()
        self._rebuild_titlebar()
        self.set_application_font("pc")

    def _rebuild_titlebar(self) -> None:
        layout = self.ui.centralwidget.layout()
        if layout is None:
            layout = QVBoxLayout(self.ui.centralwidget)

        if self.titlebar is not None:
            layout.removeWidget(self.titlebar)
            self.titlebar.deleteLater()
            self.titlebar = None

        icon_pixmap = self.qt_pop.icon.get_pixmap(
            "action join left",
            self.qt_pop.style.get_colour("accent"),
        )
        icon = QIcon(icon_pixmap) if icon_pixmap and not icon_pixmap.isNull() else QIcon()

        app_name = self._setting_value(self.qt_pop.config.get_value("name"))

        self.titlebar = CustomTitleBar(
            self.qt_pop,
            self,
            app_icon=icon,
            app_name=app_name,
        )
        layout.insertWidget(0, self.titlebar)

    # ------------------------------------------------------------------
    # Palette + settings
    # ------------------------------------------------------------------
    @debug_log
    def setup_palette(self) -> None:
        def load_palette():
            grid = QGridLayout()
            grid.setSpacing(5)
            grid.setContentsMargins(5, 5, 5, 5)
            columns = 5

            for i, (item, hex_val) in enumerate(self.qt_pop.style.colour_map().items()):
                row = i // columns
                col = i % columns
                grid.addWidget(ColorDisplayWidget(hex_val, item), row, col)

            old_layout = self.ui.p_frame.layout()
            if old_layout is not None:
                QWidget().setLayout(old_layout)

            self.ui.p_frame.setLayout(grid)

        load_palette()

    @debug_log
    def setup_settings(self) -> None:
        toolbox = self.ui.settingsTB
        while toolbox.count() > 0:
            toolbox.removeItem(0)

        grouped_settings: dict[str, list[SettingItem]] = {}
        for key, item in self.qt_pop.config.data.configuration.user.items():
            grouped_settings.setdefault(item.group, []).append(item)

        for group_name, items in grouped_settings.items():
            list_widget = QListWidget()
            list_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

            for item in items:
                self.qt_pop.log.info(f"Loading setting {item.name}, value: {item.value}")
                custom_widget = SettingItemWidget(item)
                list_item = QListWidgetItem(list_widget)
                hint = custom_widget.sizeHint()
                hint.setHeight(hint.height() + 10)
                list_item.setSizeHint(hint)
                list_widget.addItem(list_item)
                list_widget.setItemWidget(list_item, custom_widget)

            toolbox.addItem(list_widget, group_name)

        static_widget = QListWidget()
        for key, value in self.qt_pop.config.data.configuration.static.items():
            self.qt_pop.log.info(f"Loading static setting {key}, value: {value}")
            item = SettingItem(key, key, value, [], "Application static setting", "text", "user", "Static", "")
            custom_widget = SettingItemWidget(item)
            list_item = QListWidgetItem(static_widget)
            hint = custom_widget.sizeHint()
            hint.setHeight(hint.height() + 10)
            list_item.setSizeHint(hint)
            static_widget.addItem(list_item)
            static_widget.setItemWidget(list_item, custom_widget)

        toolbox.addItem(static_widget, "Static Settings")

        icon_color = self.qt_pop.style.get_colour("accent")
        for i in range(toolbox.count()):
            pixmap = self.qt_pop.icon.get_pixmap("app settings", icon_color)
            if pixmap and not pixmap.isNull():
                toolbox.setItemIcon(i, QIcon(pixmap))

    # ------------------------------------------------------------------
    # Style + settings persistence
    # ------------------------------------------------------------------
    def apply_style(self) -> None:
        accent = self.qt_pop.config.get_value("accent")
        support = self.qt_pop.config.get_value("support")
        neutral = self.qt_pop.config.get_value("neutral")
        theme = self.qt_pop.config.get_value("theme")
        self.qt_pop.style.initialise(accent.value, support.value, neutral.value, theme.value)

        qss = self.ui.cqss.toPlainText()
        translated_qss = self.qt_pop.qss.process(qss)
        self.setStyleSheet(translated_qss)
        self.setPalette(self.qt_pop.style.get_palette())
        self.ui.tqss.setText(translated_qss)

    @Slot()
    @debug_log
    def save_settings(self) -> None:
        toolbox = self.ui.settingsTB

        for i in range(toolbox.count()):
            page_widget = toolbox.widget(i)
            for row in range(page_widget.count()):
                list_item = page_widget.item(row)
                custom_widget = page_widget.itemWidget(list_item)
                if not custom_widget:
                    continue

                setting_item = custom_widget.item
                new_value = setting_item.value
                self.qt_pop.config.set_value(setting_item.shortname, new_value)
                setting_item.value = new_value

        if hasattr(self.qt_pop.config, "save"):
            self.qt_pop.config.save()

        self.qt_pop.log.info("All settings saved successfully.")
        self.qt_pop.log.info("Applying settings...")
        self.refresh_ui()
        self.qt_pop.log.info("All settings applied successfully.")

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------
    @debug_log
    def setup_logging(self) -> None:
        def on_log(timestamp: str, message: str, level: str = "INFO", color: str = ""):
            self.ui.statusbar.setStyleSheet(f"QStatusBar{{color: {color}; }}")
            self.ui.statusbar.showMessage(message, 5000)

        if self.log_widget is None:
            self.log_widget = QLogWidget(self.qt_pop)
            self.log_widget.table.setFont(self.qt_pop.font.get_font("log"))
            self.ui.log.layout().addWidget(self.log_widget)
            self.qt_pop.log.signal.connect(self.log_widget.append_log)
            self.qt_pop.log.signal.connect(on_log)

        if not self._logging_initialised:
            self.qt_pop.log.info("Running log test messages...")
            self.qt_pop.log.warning("This is a warning message.")
            self.qt_pop.log.error("This is an error message.")
            self.qt_pop.log.info("This is an info message.")
            self.qt_pop.log.debug("This is a debug message.")
            self.qt_pop.log.critical("This is a critical message.")
            self._logging_initialised = True

    # ------------------------------------------------------------------
    # QSS editor
    # ------------------------------------------------------------------
    def setup_qss(self) -> None:
        qss_path_setting = self.qt_pop.config.get_value("qss_path")
        qss_path = self._setting_value(qss_path_setting)
        default_qss = ""

        if not self._qss_initialised and qss_path:
            file = QFile(qss_path)
            if file.exists() and file.open(QFile.ReadOnly | QFile.Text):
                default_qss = file.readAll().data().decode("utf-8")
                file.close()
            else:
                self.qt_pop.log.warning(f"Unable to open QSS file: {qss_path}")

            self.ui.cqss.setText(default_qss)
            self._qss_initialised = True

        self.ui.cqss.setFont(self.qt_pop.font.get_font("log", 10))
        self.ui.tqss.setFont(self.qt_pop.font.get_font("log", 10))
        self.apply_qss_from_editor()

    def apply_qss_from_editor(self) -> None:
        raw_qss = self.ui.cqss.toPlainText()
        translated = self.qt_pop.qss.process(raw_qss)
        self.ui.tqss.setText(translated)
        self.qt_pop.qss.set_style(translated)
        self.setStyleSheet(translated)
        self.qt_pop.log.debug("Applied translated QSS.")

    def load_qss_from_file(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open QSS File",
            "",
            "QSS Files (*.qss);;All Files (*)",
        )
        if not file_path:
            return

        with open(file_path, "r", encoding="utf-8") as qss_file:
            qss_content = qss_file.read()
        self.ui.cqss.setText(qss_content)
        self.qt_pop.log.info(f"Loaded QSS file: {file_path}")
        self.apply_qss_from_editor()

    # ------------------------------------------------------------------
    # Fonts
    # ------------------------------------------------------------------
    def resizeEvent(self, event):
        super().resizeEvent(event)

    def setup_fonts(self) -> None:
        lw = self.ui.fontLW
        lw.clear()
        lw.setSpacing(6)
        self.load_add_font(lw)
        self.load_font_cards(lw)

    def load_add_font(self, lw: QListWidget) -> None:
        add_card = AddFontCard(self.add_font_callback)
        add_item = QListWidgetItem(lw)
        hint = add_card.sizeHint()
        hint.setHeight(hint.height() + 20)
        add_item.setSizeHint(hint)
        lw.addItem(add_item)
        lw.setItemWidget(add_item, add_card)

    def load_font_cards(self, lw: QListWidget) -> None:
        font_map = self.qt_pop.font.get_font_map()
        for tag, info in font_map.items():
            card = FontCard(info["family"], tag, info["size"], self.set_application_font)
            item = QListWidgetItem(lw)
            hint = card.sizeHint()
            hint.setHeight(hint.height() + 10)
            item.setSizeHint(hint)
            lw.addItem(item)
            lw.setItemWidget(item, card)

    def add_font_callback(self, font_path, tag, size):
        self.qt_pop.font.load_font(font_path, tag, size)
        lw = self.ui.fontLW
        lw.clear()
        lw.setSpacing(6)
        self.load_add_font(lw)
        self.load_font_cards(lw)

    def set_application_font(self, tag: str, size: int | None = None) -> None:
        font = self.qt_pop.font.get_font(tag)
        if font is None:
            self.qt_pop.log.warning(f"Font tag '{tag}' is not registered.")
            return

        if size is not None:
            font.setPointSize(size)

        app = QApplication.instance()
        if app is not None:
            app.setFont(font)

    # ------------------------------------------------------------------
    # Other widgets
    # ------------------------------------------------------------------
    def setup_home(self) -> None:
        if self.home is None:
            self.home = MinimalAIHome(
                qt_pop=self.qt_pop,
                app_name=self._setting_value(self.qt_pop.config.get_value("name")),
                tagline="Vivid tools. Joyful creation.",
                version=self._setting_value(self.qt_pop.config.get_value("version")),
                description=(
                    "A cutting-edge desktop application designed for creative professionals, "
                    "offering a suite of powerful tools to bring your ideas to life with ease and precision."
                ),
                svg_data=None,
            )
            self.ui.home.layout().addWidget(self.home)

    def setup_icons(self) -> None:
        icon_path_value = self._setting_value(self.qt_pop.config.get_value("icon_path"))
        icon_layout = self.ui.icons.layout()
        if icon_layout is None:
            icon_layout = QVBoxLayout(self.ui.icons)

        if self.icon_widget is not None:
            icon_layout.removeWidget(self.icon_widget)
            self.icon_widget.deleteLater()
            self.icon_widget = None

        if not icon_path_value or not os.path.isdir(icon_path_value):
            self.qt_pop.log.warning(f"Icon path does not exist: {icon_path_value}")
            return

        self.icon_widget = IconBrowserWidget(
            qt_pop=self.qt_pop,
            images_path=icon_path_value,
            parent=self,
        )
        icon_layout.addWidget(self.icon_widget)

