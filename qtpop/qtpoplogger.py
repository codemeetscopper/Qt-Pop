import logging
import functools
import inspect
import sys

from PySide6.QtCore import QObject, Signal

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    # fallback if colorama is missing
    class Fore:
        CYAN = GREEN = YELLOW = RED = MAGENTA = ""
    class Style:
        BRIGHT = RESET_ALL = ""


# --------------------------------------------
# Qt Signal Emitter for Log Messages
# --------------------------------------------
class QtLogEmitter(QObject):
    log_emitted = Signal(str, str)  # message, level


# --------------------------------------------
# Custom Formatter with Colour Support
# --------------------------------------------
class ColorFormatter(logging.Formatter):
    LEVEL_COLOURS = {
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.MAGENTA + Style.BRIGHT,
    }

    def format(self, record):
        # compute asctime safely
        record.asctime = self.formatTime(record, self.datefmt)
        record.message = record.getMessage()

        color = self.LEVEL_COLOURS.get(record.levelno, "")
        level = f"{color}{record.levelname:<8}{Style.RESET_ALL}"
        formatted = f"|  {level} | {record.asctime} | {record.message}"
        return formatted


# --------------------------------------------
# Logger Implementation
# --------------------------------------------
class QtPopLogger:
    """Enhanced logger with console colors, formatted output, and Qt signal."""

    def __init__(self, name="QtPop", level=logging.DEBUG, log_to_file=False, file_path="qtpop.log"):
        self._logger = logging.getLogger(name)
        self._logger.setLevel(level)
        self._emitter = QtLogEmitter()

        # Avoid adding handlers multiple times
        if not self._logger.handlers:
            formatter = ColorFormatter("%(asctime)s - %(levelname)s - %(message)s")

            # Console handler
            ch = logging.StreamHandler(sys.stdout)
            ch.setLevel(level)
            ch.setFormatter(formatter)
            self._logger.addHandler(ch)

            # Optional file handler
            if log_to_file:
                fh = logging.FileHandler(file_path)
                fh.setLevel(level)
                file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
                fh.setFormatter(file_formatter)
                self._logger.addHandler(fh)

        # Connect internal handler for signal emission
        self._attach_signal_handler()

    # -------------------------------------------------
    # Attach handler to emit log signals to Qt UI
    # -------------------------------------------------
    def _attach_signal_handler(self):
        class SignalHandler(logging.Handler):
            def __init__(self, emitter):
                super().__init__()
                self.emitter = emitter

            def emit(self, record):
                msg = self.format(record)
                level = record.levelname
                self.emitter.log_emitted.emit(msg, level)

        signal_handler = SignalHandler(self._emitter)
        signal_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        self._logger.addHandler(signal_handler)

    # -------------------------------------------------
    # Qt signal accessor
    # -------------------------------------------------
    @property
    def signal(self):
        """Returns the Qt signal emitter (connect to `log_emitted`)."""
        return self._emitter.log_emitted

    # -------------------------------------------------
    # Logging methods
    # -------------------------------------------------
    def debug(self, msg, *args, **kwargs):
        self._logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self._logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self._logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self._logger.error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self._logger.critical(msg, *args, **kwargs)


# --------------------------------------------
# Global Logger Instance
# --------------------------------------------
qt_logger = QtPopLogger()


# --------------------------------------------
# Decorator for function tracing
# --------------------------------------------
def debug_log(func):
    """Decorator to log function arguments and return value at debug level."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        arg_names = inspect.getfullargspec(func).args
        args_dict = dict(zip(arg_names, args))
        args_dict.update(kwargs)
        qt_logger.debug(f"{func.__name__} | args: {args_dict}")
        result = func(*args, **kwargs)
        qt_logger.debug(f"{func.__name__} | return: {result}")
        return result
    return wrapper
