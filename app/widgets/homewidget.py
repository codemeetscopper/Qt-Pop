import random
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import (
    QPainter, QColor, QFont, QPen, QBrush
)
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout
from PySide6.QtSvg import QSvgRenderer
from qtpop import QtPop


def _q(hexval): return QColor(hexval)


class MinimalAIHome(QWidget):
    def __init__(self, qt_pop: QtPop, app_name, tagline, version, description,
                 icon_path=None, svg_data=None, icon_size=128, parent=None):
        super().__init__(parent)
        self.qt_pop = qt_pop
        self.app_name = app_name
        self.tagline = tagline
        self.version = version
        self.description = description.strip()
        self.icon_size = icon_size
        self._generate_geometry_cache()

        # self._render_icon(icon_path, svg_data)
        self._build_ui()

    # -----------------------------------------
    def _generate_geometry_cache(self, count=50):
        """
        Generate random hollow geometry positions across the whole widget.
        """
        self.geos = []
        for _ in range(count):
            t = random.choice(["circle", "line", "rect"])
            # Full width/height now
            x = random.uniform(0.0, 1.0)
            y = random.uniform(0.0, 1.0)
            s = random.uniform(20, 70)  # larger shapes
            self.geos.append((t, x, y, s))

    # -----------------------------------------
    def _render_icon(self, icon_path, svg_data):
        renderer = QSvgRenderer()
        if icon_path:
            renderer.load(icon_path)
        elif svg_data:
            renderer.load(svg_data.encode())
        else:
            renderer.load("""
            <svg xmlns="http://www.w3.org/2000/svg" width="256" height="256">
              <circle cx="128" cy="128" r="90" fill="#AAA"/>
            </svg>
            """.encode())

        from PySide6.QtGui import QPixmap, QPainter
        self.icon_pix = QPixmap(self.icon_size, self.icon_size)
        self.icon_pix.fill(Qt.transparent)
        p = QPainter(self.icon_pix)
        renderer.render(p, QRectF(0, 0, self.icon_size, self.icon_size))
        p.end()

    # -----------------------------------------
    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(45, 150, 0, 150)


        col = QVBoxLayout()
        col.setSpacing(10)

        icon = QLabel()
        icon.setPixmap(self.qt_pop.icon.get_pixmap('action join left',
                                                   self.qt_pop.style.get_colour('accent'),
                                                   self.icon_size))
        icon.setFixedSize(self.icon_size, self.icon_size)
        icon.setScaledContents(True)
        col.addWidget(icon, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        title = QLabel(self.app_name)
        ft = QFont(); ft.setPointSize(26); ft.setBold(True)
        title.setFont(ft)
        col.addWidget(title, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        tagline = QLabel(self.tagline)
        fs = QFont(); fs.setPointSize(12)
        tagline.setFont(fs)
        col.addWidget(tagline, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        desc = QLabel(self.description)
        fd = QFont(); fd.setPointSize(11)
        desc.setFont(fd)
        desc.setWordWrap(True)
        # desc.setMaximumWidth(800)
        col.addWidget(desc, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        v = QLabel(f"Version {self.version}")
        fv = QFont(); fv.setPointSize(9)
        v.setFont(fv)
        col.addWidget(v)

        layout.addLayout(col, 1)
        layout.addStretch(2)
        self.setLayout(layout)

    # -----------------------------------------
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Theme colors from engine
        bg = _q(self.qt_pop.style.get_colour('bg'))
        accent = _q(self.qt_pop.style.get_colour('accent'))
        support = _q(self.qt_pop.style.get_colour('support'))
        neutral = _q(self.qt_pop.style.get_colour('neutral'))

        # Background
        painter.fillRect(self.rect(), bg)

        w, h = self.width(), self.height()

        # Larger hollow geometric structure — full background spread
        for t, rx, ry, s in self.geos:
            px = w * rx
            py = h * ry
            size = s * 3.5  # ⬅ bigger shapes

            if t == "circle":
                painter.setBrush(Qt.NoBrush)
                painter.setPen(QPen(
                    QColor(neutral.red(), neutral.green(), neutral.blue(), 55),
                    1.2
                ))
                painter.drawEllipse(QPointF(px, py), size * 0.45, size * 0.45)

            elif t == "rect":
                painter.setBrush(Qt.NoBrush)
                painter.setPen(QPen(
                    QColor(support.red(), support.green(), support.blue(), 50),
                    1.1
                ))
                painter.drawRoundedRect(QRectF(px, py, size, size * 0.55), 10, 10)

            elif t == "line":
                painter.setBrush(Qt.NoBrush)
                painter.setPen(QPen(
                    QColor(accent.red(), accent.green(), accent.blue(), 70),
                    1.3
                ))
                painter.drawLine(px, py, px + size * 0.9, py - size * 0.35)

        painter.end()
