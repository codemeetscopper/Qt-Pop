# qlogwidget.py
"""
QLogWidget - polished, modern PySide6 log viewer widget (no QSS).
Features:
 - Minimal separators (no grid lines)
 - Uniform font weight
 - Auto-trim leading whitespace of messages
 - Millisecond timestamps (default)
 - Hover tooltip showing full raw log
 - Level filter, regex search, pause, autoscroll, wrap toggle, export/copy/clear
 - Efficient model-backed storage + bounded circular buffer
 - No external dependencies
"""

from collections import deque
import csv
import re
from datetime import datetime
from typing import Iterable, Tuple

from PySide6.QtCore import Qt, QSortFilterProxyModel, QModelIndex, QEvent, QPoint
from PySide6.QtGui import QStandardItemModel, QStandardItem, QFont, QColor, QCursor, QGuiApplication
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QComboBox, QLineEdit, QTableView,
    QHeaderView, QLabel, QToolButton, QFileDialog, QMessageBox, QAbstractItemView,
    QCheckBox, QSpinBox, QTextEdit, QDialog, QApplication, QToolTip
)

# Roles for data storage on items
ROLE_TIMESTAMP = Qt.UserRole + 1
ROLE_LEVEL = Qt.UserRole + 2
ROLE_MESSAGE = Qt.UserRole + 3
ROLE_RAW = Qt.UserRole + 4  # raw message (unmodified)
ROLE_COLOR = Qt.UserRole + 5

# Level order and default colors (adaptable to current palette)
_LEVEL_ORDER = {"DEBUG": 10, "INFO": 20, "WARNING": 30, "ERROR": 40, "CRITICAL": 50}
# Use palette-trusting colors: choose conservative RGB that's readable on light/dark
_LEVEL_COLORS = {
    "DEBUG": QColor(128, 128, 128),
    "INFO": QColor(40, 120, 220),
    "WARNING": QColor(200, 120, 30),
    "ERROR": QColor(200, 45, 45),
    "CRITICAL": QColor(180, 40, 160),
}


class LogFilterProxy(QSortFilterProxyModel):
    """Filters rows by minimum level and an optional regex applied to timestamp/message."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.min_level_value = 0
        self.search_regex = None  # compiled regex or None

    def set_min_level(self, level_name: str):
        self.min_level_value = _LEVEL_ORDER.get(level_name.upper(), 0)
        self.invalidateFilter()

    def set_search(self, pattern: str):
        if not pattern:
            self.search_regex = None
        else:
            try:
                self.search_regex = re.compile(pattern, re.IGNORECASE)
            except re.error:
                # fallback to literal substring search when invalid regex
                self.search_regex = re.compile(re.escape(pattern), re.IGNORECASE)
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        model = self.sourceModel()
        idx = model.index(source_row, 0, source_parent)
        lvl = model.data(idx, ROLE_LEVEL) or ""
        lvl_val = _LEVEL_ORDER.get(lvl.upper(), 0)
        if lvl_val < self.min_level_value:
            return False

        if self.search_regex:
            ts = model.data(idx, ROLE_TIMESTAMP) or ""
            msg = model.data(idx, ROLE_MESSAGE) or ""
            return bool(self.search_regex.search(ts) or self.search_regex.search(msg))
        return True


class MessageViewerDialog(QDialog):
    def __init__(self, title: str, text: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(900, 420)
        layout = QVBoxLayout(self)
        text_edit = QTextEdit(self)
        text_edit.setReadOnly(True)
        text_edit.setPlainText(text)
        layout.addWidget(text_edit)
        btn = QPushButton("Close")
        btn.clicked.connect(self.accept)
        footer = QHBoxLayout()
        footer.addStretch(1)
        footer.addWidget(btn)
        layout.addLayout(footer)


class QLogWidget(QWidget):
    """
    Polished QLogWidget implementing user preferences:
      - minimal separators (no grid)
      - uniform font weight
      - auto-trim leading whitespace
      - millisecond timestamps
      - hover tooltip with full raw log
    Integration: widget.connect_logger(qt_logger.signal) or widget.append_log(...)
    """
    def __init__(self, parent=None, max_rows: int = 20000):
        super().__init__(parent)
        self.max_rows = max_rows
        self.buffer = deque(maxlen=max_rows)  # store tuples (ts, level, msg, raw, color)
        self.paused = False
        self.autoscroll = True

        self._setup_fonts_and_palette()
        self._build_ui()
        self._connect_signals()

        # install event filter on tableviewport to show tooltip on hover
        self.table.viewport().installEventFilter(self)

    def _setup_fonts_and_palette(self):
        # Use comfortable base font; keep same weight for all levels
        pass
        self.base_font = QFont()
        self.base_font.setPointSize(10)
        self.compact_font = QFont(self.base_font)
        self.compact_font.setPointSize(9)

    def _build_ui(self):
        self.setFont(self.base_font)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)

        # Top toolbar
        top = QHBoxLayout()
        top.setSpacing(6)
        # top.addWidget(QLabel("Level"))
        self.level_combo = QComboBox()
        self.level_combo.addItems(["ALL", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.level_combo.setCurrentText("DEBUG")
        # self.level_combo.setFixedWidth(110)
        top.addWidget(self.level_combo)

        # top.addWidget(QLabel("Filter"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("regex or substring (message/timestamp)")
        self.search_edit.setClearButtonEnabled(True)
        # self.search_edit.setFixedWidth(380)
        top.addWidget(self.search_edit)

        # Pause toggle
        self.pause_btn = QToolButton()
        self.pause_btn.setText("Pause")
        self.pause_btn.setCheckable(True)
        top.addWidget(self.pause_btn)

        top.addStretch(1)

        self.autoscroll_chk = QCheckBox("Autoscroll")
        self.autoscroll_chk.setChecked(True)
        top.addWidget(self.autoscroll_chk)

        self.wrap_chk = QCheckBox("Wrap")
        self.wrap_chk.setChecked(False)
        top.addWidget(self.wrap_chk)

        self.ts_chk = QCheckBox("Show Time")
        self.ts_chk.setChecked(True)
        top.addWidget(self.ts_chk)



        # Action buttons
        self.copy_btn = QPushButton("Copy Selected")
        self.save_btn = QPushButton("Export CSV")
        self.clear_btn = QPushButton("Clear")
        top.addWidget(self.copy_btn)
        top.addWidget(self.save_btn)
        top.addWidget(self.clear_btn)

        layout.addLayout(top)

        # Table view and models
        self.model = QStandardItemModel(0, 3, self)
        self.model.setHorizontalHeaderLabels(["Time", "Level", "Message"])
        self.proxy = LogFilterProxy(self)
        self.proxy.setSourceModel(self.model)

        self.table = QTableView()
        self.table.setModel(self.proxy)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.table.verticalHeader().setVisible(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setHighlightSections(False)

        # Minimal visual style: no grid lines
        self.table.setShowGrid(False)
        # keep uniform font weight — don't set bold anywhere
        self.table.setAlternatingRowColors(True)
        self.table.setWordWrap(False)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSortingEnabled(False)
        self.table.setFocusPolicy(Qt.StrongFocus)

        # compact row height
        self.table.verticalHeader().setDefaultSectionSize(22)

        layout.addWidget(self.table)

        # Bottom status
        bottom = QHBoxLayout()
        self.count_label = QLabel("0 entries")
        bottom.addWidget(self.count_label)
        bottom.addStretch(1)
        bottom.addWidget(QLabel("Max rows:"))
        self.max_spin = QSpinBox()
        self.max_spin.setRange(100, 1000000)
        self.max_spin.setSingleStep(100)
        self.max_spin.setValue(self.max_rows)
        bottom.addWidget(self.max_spin)
        layout.addLayout(bottom)

    def _connect_signals(self):
        self.level_combo.currentTextChanged.connect(lambda t: self.proxy.set_min_level(t))
        self.search_edit.textChanged.connect(self.proxy.set_search)
        self.pause_btn.toggled.connect(self._on_pause_toggled)
        self.autoscroll_chk.toggled.connect(self._on_autoscroll_toggled)
        self.wrap_chk.toggled.connect(self._on_wrap_toggled)
        self.ts_chk.toggled.connect(self._on_timestamp_toggled)
        self.clear_btn.clicked.connect(self.clear)
        self.copy_btn.clicked.connect(self.copy_selected)
        self.save_btn.clicked.connect(self.export_csv)
        self.max_spin.valueChanged.connect(self._on_max_rows_changed)
        self.table.doubleClicked.connect(self._on_row_doubleclicked)

    # -----------------------
    # Signal integration
    # -----------------------
    def connect_logger(self, qt_signal):
        """
        Connect a Qt signal that emits (timestamp, message, level, color).
        Example: self.log_widget.connect_logger(qt_logger.signal)
        """
        try:
            # best-effort disconnect to avoid duplicate connections
            try:
                qt_signal.disconnect()
            except Exception:
                pass
            qt_signal.connect(self._on_external_log)
        except Exception as e:
            raise RuntimeError(f"Failed to connect logger signal: {e}")

    def append_log(self, timestamp: str, message: str, level: str = "INFO", color: str = ""):
        """
        Append a log entry. Trims leading whitespace from message as requested.
        Timestamp will be used verbatim if provided; otherwise current time with milliseconds.
        """
        # sanitize
        if timestamp is None or timestamp == "":
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]  # milliseconds
        else:
            ts = str(timestamp)

        raw_msg = str(message)
        # auto-trim leading whitespace; preserve internal/newline whitespace
        trimmed = raw_msg.lstrip()
        lvl = (level or "INFO").upper()

        # push to circular buffer
        self.buffer.append((ts, lvl, trimmed, raw_msg, color))

        if not self.paused:
            self._push_to_model(ts, lvl, trimmed, raw_msg, color)

    def _on_external_log(self, timestamp, message, level, color):
        # convert to strings robustly
        try:
            ts = str(timestamp)
        except Exception:
            ts = ""
        try:
            msg = str(message)
        except Exception:
            msg = repr(message)
        try:
            lvl = str(level)
        except Exception:
            lvl = "INFO"
        self.append_log(ts, msg, lvl, color)

    # -----------------------
    # Model / view handling
    # -----------------------
    def _push_to_model(self, ts: str, lvl: str, msg: str, raw: str, color: str):
        # prune if model is already at capacity
        if self.model.rowCount() >= self.max_rows:
            remove_count = max(1, self.model.rowCount() - self.max_rows + 1)
            for _ in range(remove_count):
                self.model.removeRow(0)

        # prepare items
        t_item = QStandardItem(ts if ts is not None else "")
        l_item = QStandardItem(lvl)
        m_item = QStandardItem(msg)

        # store roles
        for it in (t_item, l_item, m_item):
            it.setData(ts, ROLE_TIMESTAMP)
            it.setData(lvl, ROLE_LEVEL)
            it.setData(msg, ROLE_MESSAGE)
            it.setData(raw, ROLE_RAW)
            it.setData(color, ROLE_COLOR)
            it.setFont(self.compact_font)

        # determine color for display (use provided map)
        qcolor = _LEVEL_COLORS.get(lvl.upper(), QColor(150, 150, 150))
        t_item.setForeground(qcolor)
        l_item.setForeground(qcolor)
        m_item.setForeground(qcolor)

        # insert row
        row_pos = self.model.rowCount()
        self.model.insertRow(row_pos, [t_item, l_item, m_item])
        self.count_label.setText(f"{self.model.rowCount()} entries")

        if self.autoscroll:
            self.table.scrollToBottom()

    # -----------------------
    # Controls
    # -----------------------
    def _on_pause_toggled(self, state: bool):
        self.paused = state
        if not self.paused:
            # rebuild the model from buffer tail to ensure consistency and ordering
            tail = list(self.buffer)[-self.max_rows:]
            self.model.removeRows(0, self.model.rowCount())
            for ts, lvl, trimmed, raw, color in tail:
                # use _push_to_model but avoid re-pruning since buffer already respects max_rows
                t_item = QStandardItem(ts)
                l_item = QStandardItem(lvl)
                m_item = QStandardItem(trimmed)
                for it in (t_item, l_item, m_item):
                    it.setData(ts, ROLE_TIMESTAMP)
                    it.setData(lvl, ROLE_LEVEL)
                    it.setData(trimmed, ROLE_MESSAGE)
                    it.setData(raw, ROLE_RAW)
                    it.setData(color, ROLE_COLOR)
                    it.setFont(self.compact_font)
                qcolor = _LEVEL_COLORS.get(lvl.upper(), QColor(150, 150, 150))
                t_item.setForeground(qcolor)
                l_item.setForeground(qcolor)
                m_item.setForeground(qcolor)
                self.model.appendRow([t_item, l_item, m_item])
            self.count_label.setText(f"{self.model.rowCount()} entries")

    def _on_autoscroll_toggled(self, s: bool):
        self.autoscroll = s

    def _on_wrap_toggled(self, s: bool):
        self.table.setWordWrap(s)
        if s:
            # allow rows to expand moderately when wrapping
            self.table.verticalHeader().setDefaultSectionSize(28)
        else:
            self.table.verticalHeader().setDefaultSectionSize(22)

    def _on_timestamp_toggled(self, s: bool):
        self.table.setColumnHidden(0, not s)
        if s:
            self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        else:
            self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)

    def clear(self):
        self.model.removeRows(0, self.model.rowCount())
        self.buffer.clear()
        self.count_label.setText("0 entries")

    def copy_selected(self):
        sel = self.table.selectionModel().selectedRows()
        if not sel:
            QMessageBox.information(self, "Copy Selected", "No rows selected.")
            return
        lines = []
        for proxy_index in sel:
            src_index = self.proxy.mapToSource(proxy_index)
            ts = self.model.data(self.model.index(src_index.row(), 0), ROLE_TIMESTAMP) or ""
            lvl = self.model.data(self.model.index(src_index.row(), 1), ROLE_LEVEL) or ""
            msg = self.model.data(self.model.index(src_index.row(), 2), ROLE_MESSAGE) or ""
            lines.append(f"{ts} | {lvl} | {msg}")
        clipboard = QGuiApplication.clipboard()
        clipboard.setText("\n".join(lines))
        QMessageBox.information(self, "Copy Selected", f"Copied {len(lines)} rows to clipboard.")

    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Logs to CSV", "logs.csv", "CSV Files (*.csv);;All Files (*)")
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "level", "message"])
                for row in range(self.model.rowCount()):
                    ts = self.model.item(row, 0).text()
                    lvl = self.model.item(row, 1).text()
                    msg = self.model.item(row, 2).text()
                    writer.writerow([ts, lvl, msg])
            QMessageBox.information(self, "Export CSV", f"Exported {self.model.rowCount()} rows to {path}")
        except Exception as e:
            QMessageBox.critical(self, "Export CSV", f"Failed to export logs: {e}")

    def _on_row_doubleclicked(self, proxy_index: QModelIndex):
        src = self.proxy.mapToSource(proxy_index)
        ts = self.model.data(self.model.index(src.row(), 0), ROLE_TIMESTAMP) or ""
        lvl = self.model.data(self.model.index(src.row(), 1), ROLE_LEVEL) or ""
        raw = self.model.data(self.model.index(src.row(), 2), ROLE_RAW) or ""
        dlg = MessageViewerDialog(f"{ts} | {lvl}", raw, self)
        dlg.exec()

    def _on_max_rows_changed(self, val: int):
        self.max_rows = val
        # change buffer capacity while preserving recent items
        new_buf = deque(self.buffer, maxlen=val)
        self.buffer = new_buf
        # prune model if needed
        while self.model.rowCount() > val:
            self.model.removeRow(0)

    # -----------------------
    # Event filter for hover tooltip showing full raw log
    # -----------------------
    def eventFilter(self, obj, event):
        if obj is self.table.viewport():
            if event.type() == QEvent.MouseMove:
                pos: QPoint = event.pos()
                index = self.table.indexAt(pos)
                if index.isValid():
                    src_index = self.proxy.mapToSource(index)
                    raw = self.model.data(self.model.index(src_index.row(), 2), ROLE_RAW) or ""
                    ts = self.model.data(self.model.index(src_index.row(), 0), ROLE_TIMESTAMP) or ""
                    lvl = self.model.data(self.model.index(src_index.row(), 1), ROLE_LEVEL) or ""
                    # build tooltip text (short, but full raw message included)
                    tooltip = f"{ts} | {lvl}\n{raw}"
                    QToolTip.showText(self.table.viewport().mapToGlobal(pos), tooltip, self.table.viewport())
                else:
                    QToolTip.hideText()
            elif event.type() in (QEvent.Leave, QEvent.FocusOut):
                QToolTip.hideText()
        return super().eventFilter(obj, event)

    # -----------------------
    # Helper: append a batch of rows
    # -----------------------
    def append_batch(self, entries: Iterable[Tuple[str, str, str, str]]):
        """
        entries: iterable of (timestamp, message, level, color)
        safe to call with many items; will respect max_rows
        """
        for ts, msg, lvl, color in entries:
            self.append_log(ts, msg, lvl, color)


# -----------------------
# Demo / usage example
# -----------------------
if __name__ == "__main__":
    import sys
    import random
    app = QApplication(sys.argv)
    w = QLogWidget()
    w.resize(1000, 480)
    w.show()

    # demo messages
    levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    for i in range(60):
        lvl = random.choice(levels)
        raw = "     " + f"Demo message {i} | level={lvl} | extra details and maybe a long trace..."
        w.append_log("", raw, lvl, "")
    sys.exit(app.exec())
