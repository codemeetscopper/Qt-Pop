# impressive_hero.py
from __future__ import annotations
import sys
import math
import random
from dataclasses import dataclass
from typing import List

from PySide6.QtCore import (
    Qt, QTimer, QRectF, QPointF, QSize, QPropertyAnimation, QEasingCurve, QObject, Property
)
from PySide6.QtGui import (
    QPainter, QColor, QFont, QPixmap, QPainterPath, QPen, QBrush, QLinearGradient,
    QRadialGradient, QTransform
)
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QHBoxLayout, QVBoxLayout, QPushButton, QSizePolicy,
    QGraphicsDropShadowEffect, QGraphicsBlurEffect, QFrame
)
from PySide6.QtSvg import QSvgRenderer


# -------------------------
# Particle model
# -------------------------
@dataclass
class Particle:
    pos: QPointF
    vel: QPointF
    size: float
    color: QColor
    life: float
    max_life: float
    wobble: float


# -------------------------
# Background layer: gradient glow + particles (painted)
# -------------------------
class ParticleBackground(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.particles: List[Particle] = []
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_particles)
        self.timer.start(16)  # ~60 FPS
        self.spawn_rate = 4  # particles per tick
        self.mouse_parallax = QPointF(0, 0)
        self.setContentsMargins(0, 0, 0, 0)

        # blur effect: we'll animate blurRadius externally
        self.blur_effect = QGraphicsBlurEffect(self)
        self.blur_effect.setBlurRadius(10.0)
        self.setGraphicsEffect(self.blur_effect)

    def sizeHint(self):
        return QSize(1200, 500)

    def setParallax(self, p: QPointF):
        # parallax vector from parent (small values)
        self.mouse_parallax = p

    def update_particles(self):
        w, h = self.width(), self.height()
        # spawn new particles
        for _ in range(self.spawn_rate):
            x = random.uniform(w * 0.1, w * 0.9)
            y = random.uniform(h * 0.2, h * 0.8)
            angle = random.uniform(-math.pi, math.pi)
            speed = random.uniform(0.2, 1.2)
            vel = QPointF(math.cos(angle) * speed, math.sin(angle) * speed * 0.6)
            sz = random.uniform(6.0, 22.0)
            hue = random.choice([190, 200, 210, 260, 280, 320])
            saturation = random.randint(180, 255)
            color = QColor.fromHsv(hue, saturation, random.randint(200, 255), random.randint(110, 220))
            life = random.uniform(2.0, 6.0)
            wobble = random.uniform(0.2, 1.6)
            p = Particle(QPointF(x, y), vel, sz, color, life, life, wobble)
            self.particles.append(p)

        # update existing
        new_particles = []
        for p in self.particles:
            # wobble + velocity
            p.pos += p.vel
            p.pos.setX(p.pos.x() + math.sin(p.max_life - p.life) * p.wobble)
            p.pos.setY(p.pos.y() + math.cos(p.max_life - p.life) * (p.wobble * 0.3))
            p.life -= 0.033
            # fade out
            if p.life > 0 and 0 <= p.pos.x() <= w and 0 <= p.pos.y() <= h:
                new_particles.append(p)
        self.particles = new_particles
        self.update()

    def paintEvent(self, ev):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w, h = self.width(), self.height()

        # Layer 1: deep diagonal gradient
        grad = QLinearGradient(0, 0, w, h)
        grad.setColorAt(0.0, QColor(18, 10, 40))
        grad.setColorAt(0.5, QColor(12, 6, 24))
        grad.setColorAt(1.0, QColor(6, 4, 12))
        painter.fillRect(self.rect(), grad)

        # Layer 2: soft radial orbs (parallax shifted)
        orb_center = QPointF(w * 0.75 + self.mouse_parallax.x() * 60, h * 0.3 + self.mouse_parallax.y() * 40)
        rgrad = QRadialGradient(orb_center, w * 0.5)
        rgrad.setColorAt(0.0, QColor(0, 150, 255, 90))
        rgrad.setColorAt(0.25, QColor(150, 0, 255, 35))
        rgrad.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setBrush(rgrad)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(orb_center, w * 0.6, h * 0.5)

        # Layer 3: small glowing accents (parallax)
        accent_center = QPointF(w * 0.18 + self.mouse_parallax.x() * -40, h * 0.55 + self.mouse_parallax.y() * -35)
        agr = QRadialGradient(accent_center, w * 0.18)
        agr.setColorAt(0.0, QColor(255, 120, 180, 130))
        agr.setColorAt(1.0, QColor(255, 120, 180, 0))
        painter.setBrush(agr)
        painter.drawEllipse(accent_center, w * 0.22, h * 0.18)

        # Layer 4: particles (playful / bright)
        for p in self.particles:
            life_ratio = max(0.0, min(1.0, p.life / p.max_life))
            alpha = int(p.color.alpha() * life_ratio)
            c = QColor(p.color)
            c.setAlpha(alpha)
            # draw as blurred circle - emulate glow by painting multiple concentric circles
            outer = p.size * (1.8 + (1.0 - life_ratio))
            brush = QBrush(c)
            painter.setBrush(brush)
            painter.setPen(Qt.NoPen)
            # main
            painter.drawEllipse(p.pos, p.size * 0.8, p.size * 0.8)
            # subtle halo
            halo_color = QColor(c)
            halo_color.setAlpha(int(alpha * 0.35))
            painter.setBrush(halo_color)
            painter.drawEllipse(p.pos, outer, outer * 0.8)

        painter.end()


# -------------------------
# Hero card with content + animations
# -------------------------
class AnimatedIconLabel(QLabel):
    def __init__(self, svg_data: str | None = None, icon_size=128, parent=None):
        super().__init__(parent)
        self.icon_size = icon_size
        self.setFixedSize(icon_size, icon_size)
        self.setScaledContents(True)
        self._svg = svg_data
        self._pix = self._render_svg(svg_data)
        self.setPixmap(self._pix)

        # animation state
        self._scale = 0.02
        self._opacity = 0.0

    def _render_svg(self, svg_data):
        renderer = QSvgRenderer()
        if svg_data:
            renderer.load(svg_data.encode('utf-8'))
        else:
            # default neon SVG
            default = b"""
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 240">
              <defs>
                <linearGradient id="g" x1="0" x2="1">
                  <stop offset="0" stop-color="#3ee8ff"/>
                  <stop offset="1" stop-color="#9b59ff"/>
                </linearGradient>
              </defs>
              <rect rx="40" width="240" height="240" fill="url(#g)"/>
              <circle cx="120" cy="120" r="60" fill="#ffffffcc"/>
            </svg>
            """
            renderer.load(default)
        pix = QPixmap(self.icon_size, self.icon_size)
        pix.fill(Qt.transparent)
        painter = QPainter(pix)
        renderer.render(painter, QRectF(0, 0, self.icon_size, self.icon_size))
        painter.end()
        return pix

    # expose properties for animations via QObject property pattern
    def getScale(self):
        return self._scale

    def setScale(self, s):
        self._scale = s
        self.update()

    def getOpacity(self):
        return self._opacity

    def setOpacity(self, o):
        self._opacity = o
        self.update()

    scale = Property(float, getScale, setScale)
    opacity = Property(float, getOpacity, setOpacity)

    def paintEvent(self, ev):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        painter.setRenderHint(QPainter.Antialiasing)

        # draw scaled pixmap centered
        w, h = self.width(), self.height()
        sx = self._scale
        sw = max(1, int(w * sx))
        sh = max(1, int(h * sx))
        # center
        x = (w - sw) / 2
        y = (h - sh) / 2
        painter.setOpacity(self._opacity)
        painter.drawPixmap(int(x), int(y), sw, sh, self._pix)
        painter.end()


class ImpressiveHero(QWidget):
    """
    Horizontal, full-width hero widget with:
      - gradient / glow background (ParticleBackground)
      - animated logo reveal
      - simulated live blur (animated blur radius)
      - parallax glow movement with mouse
      - accent particle field behind (playful)
      - fade-in entrance sequence
    """

    def __init__(self, app_name: str, tagline: str, version: str, description: str,
                 svg_data: str | None = None, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.svg_data = svg_data
        self.app_name = app_name
        self.tagline = tagline
        self.version = version
        self.description = description
        self._build_ui()
        self._wire_animations()

    def _build_ui(self):
        # Full layout: background (stacked) + foreground horizontal card
        self.setContentsMargins(0, 0, 0, 0)
        self.bg = ParticleBackground(self)
        self.bg.setGeometry(self.rect())
        self.bg.lower()

        # Foreground container (glass-like horizontal card)
        self.card = QFrame(self)
        self.card.setObjectName("hero_card")
        self.card.setContentsMargins(0, 0, 0, 0)
        self.card.setFixedHeight(240)
        # We'll size and center it in resizeEvent
        # add drop shadow
        shadow = QGraphicsDropShadowEffect(self.card)
        shadow.setBlurRadius(40)
        shadow.setOffset(0, 18)
        shadow.setColor(QColor(0, 0, 0, 180))
        self.card.setGraphicsEffect(shadow)

        # left: animated icon
        self.icon = AnimatedIconLabel(self.svg_data, icon_size=152, parent=self.card)
        icon_shadow = QGraphicsDropShadowEffect(self.icon)
        icon_shadow.setBlurRadius(40)
        icon_shadow.setOffset(0, 20)
        icon_shadow.setColor(QColor(0, 0, 0, 200))
        self.icon.setGraphicsEffect(icon_shadow)

        # right: texts
        self.title_label = QLabel(self.app_name, self.card)
        tf = QFont()
        tf.setPointSize(28)
        tf.setBold(True)
        self.title_label.setFont(tf)
        self.title_label.setAttribute(Qt.WA_TransparentForMouseEvents)

        self.tagline_label = QLabel(self.tagline, self.card)
        tg = QFont()
        tg.setPointSize(12)
        tg.setItalic(True)
        self.tagline_label.setFont(tg)
        self.tagline_label.setAttribute(Qt.WA_TransparentForMouseEvents)

        self.desc_label = QLabel(self.description, self.card)
        df = QFont()
        df.setPointSize(11)
        self.desc_label.setFont(df)
        self.desc_label.setWordWrap(True)
        self.desc_label.setAttribute(Qt.WA_TransparentForMouseEvents)

        self.version_label = QLabel(f"Version {self.version}", self.card)
        vf = QFont()
        vf.setPointSize(9)
        self.version_label.setFont(vf)
        self.version_label.setAttribute(Qt.WA_TransparentForMouseEvents)

        # CTA button
        self.cta = QPushButton("Launch App", self.card)
        self.cta.setCursor(Qt.PointingHandCursor)
        self.cta.setFixedHeight(42)
        self.cta.setMinimumWidth(160)
        # styled by painting in the card (we won't use stylesheets). But simple text is fine.

        # Layout inside card (horizontal)
        hl = QHBoxLayout(self.card)
        hl.setContentsMargins(30, 18, 30, 18)
        hl.setSpacing(28)

        left_v = QVBoxLayout()
        left_v.addStretch()
        left_v.addWidget(self.icon, 0, Qt.AlignLeft | Qt.AlignVCenter)
        left_v.addStretch()

        right_v = QVBoxLayout()
        right_v.setSpacing(6)
        right_v.addWidget(self.title_label)
        right_v.addWidget(self.tagline_label)
        right_v.addWidget(self.desc_label)
        right_v.addSpacing(6)
        bottom_row = QHBoxLayout()
        bottom_row.addWidget(self.version_label)
        bottom_row.addStretch()
        bottom_row.addWidget(self.cta)
        right_v.addLayout(bottom_row)

        hl.addLayout(left_v)
        hl.addLayout(right_v)

        # Owning layout for the main widget: we'll not use layout; we position manually
        self.fade_opacity = 0.0  # used for fade-in entrance
        self._entrance_anim = None

    def resizeEvent(self, ev):
        # position background and card centered horizontally
        self.bg.setGeometry(self.rect())
        w, h = self.width(), self.height()
        card_w = int(min(w * 0.86, 1100))
        card_h = self.card.height()
        self.card.setGeometry((w - card_w) // 2, max(40, (h - card_h) // 2), card_w, card_h)

    # --------------------------
    # Mouse / Parallax handling
    # --------------------------
    def mouseMoveEvent(self, ev):
        # compute relative mouse offset from center - normalized [-1,1]
        cx = self.width() / 2
        cy = self.height() / 2
        rx = (ev.x() - cx) / max(1, cx)
        ry = (ev.y() - cy) / max(1, cy)
        par = QPointF(rx, ry)
        # set background parallax (small factor)
        self.bg.setParallax(par * 0.35)
        # move subtle glows on card: reposition card's transform slightly
        tx = -rx * 10
        ty = -ry * 6
        t = QTransform().translate(tx, ty)
        self.card.setGraphicsEffect(self.card.graphicsEffect())  # keep shadow
        self.card.move(self.card.x() + 0, self.card.y() + 0)  # no-op to ensure repaint
        self.card.setProperty("parallaxTransform", t)  # informative; not used directly
        self.update()

    def leaveEvent(self, ev):
        # reset parallax
        self.bg.setParallax(QPointF(0, 0))

    # --------------------------
    # Animations
    # --------------------------
    def _wire_animations(self):
        # 1) Entrance fade-in (widget-level)
        self._entrance_anim = QPropertyAnimation(self, b"fadeValue")
        self._entrance_anim.setDuration(900)
        self._entrance_anim.setStartValue(0.0)
        self._entrance_anim.setEndValue(1.0)
        self._entrance_anim.setEasingCurve(QEasingCurve.OutCubic)
        # 2) Blur pulse for background (simulate live blur)
        self._blur_anim = QPropertyAnimation(self.bg.blur_effect, b"blurRadius")
        self._blur_anim.setDuration(2400)
        self._blur_anim.setStartValue(6.0)
        self._blur_anim.setEndValue(22.0)
        self._blur_anim.setEasingCurve(QEasingCurve.InOutSine)
        self._blur_anim.setLoopCount(-1)  # ping-pong via auto-reverse style
        self._blur_anim.valueChanged.connect(lambda v: self.bg.update())
        self._blur_anim.setDirection(QPropertyAnimation.Forward)
        # to ping-pong we use finished handler
        self._blur_anim.finished.connect(self._reverse_blur)

        # 3) Logo reveal scale + opacity animations (with bounce)
        self.icon_scale_anim = QPropertyAnimation(self.icon, b"scale")
        self.icon_scale_anim.setDuration(900)
        self.icon_scale_anim.setStartValue(0.05)
        self.icon_scale_anim.setEndValue(1.02)
        self.icon_scale_anim.setEasingCurve(QEasingCurve.OutBack)

        # tiny settle back to exactly 1.0
        self.icon_settle = QPropertyAnimation(self.icon, b"scale")
        self.icon_settle.setDuration(220)
        self.icon_settle.setStartValue(1.02)
        self.icon_settle.setEndValue(1.0)
        self.icon_settle.setEasingCurve(QEasingCurve.OutCubic)

        # opacity for icon
        self.icon_opacity_anim = QPropertyAnimation(self.icon, b"opacity")
        self.icon_opacity_anim.setDuration(650)
        self.icon_opacity_anim.setStartValue(0.0)
        self.icon_opacity_anim.setEndValue(1.0)
        self.icon_opacity_anim.setEasingCurve(QEasingCurve.OutCubic)

        # 4) CTA pulse animation
        self.cta_anim = QPropertyAnimation(self.cta, b"geometry")
        self.cta_anim.setDuration(1000)
        self.cta_anim.setEasingCurve(QEasingCurve.InOutSine)
        self.cta_anim.setLoopCount(-1)

        # orchestrate sequence
        # start fade-in, then start blur pulse, icon reveal etc.
        self._entrance_anim.finished.connect(self._start_secondary_animations)
        self._entrance_anim.start()

    def _reverse_blur(self):
        # reverse direction smoothly and restart
        current = self.bg.blur_effect.blurRadius()
        anim = QPropertyAnimation(self.bg.blur_effect, b"blurRadius")
        anim.setDuration(2200)
        anim.setStartValue(current)
        anim.setEndValue(6.0 if current > 12 else 22.0)
        anim.setEasingCurve(QEasingCurve.InOutSine)
        anim.finished.connect(self._reverse_blur)
        anim.start()
        # keep a reference to prevent GC
        self._blur_anim = anim

    def _start_secondary_animations(self):
        # blur loop start
        if hasattr(self, "_blur_anim") and self._blur_anim:
            try:
                self._blur_anim.start()
            except Exception:
                pass

        # icon reveal timeline
        self.icon_opacity_anim.start()
        self.icon_scale_anim.start()
        # sequence settle after scale finishes
        self.icon_scale_anim.finished.connect(lambda: self.icon_settle.start())

        # CTA pulse (animate small width change)
        rect = self.cta.geometry()
        expanded = rect.adjusted(-8, -2, 8, 2)
        self.cta_anim.setStartValue(rect)
        self.cta_anim.setEndValue(expanded)
        self.cta_anim.start()

        # subtle entrance for text via property animation on widget opacity simulated by repaint
        # We'll animate internal fade value for text rendering
        self._text_fade = 0.0
        self._text_anim = QPropertyAnimation(self, b"textFade")
        self._text_anim.setDuration(700)
        self._text_anim.setStartValue(0.0)
        self._text_anim.setEndValue(1.0)
        self._text_anim.setEasingCurve(QEasingCurve.OutCubic)
        self._text_anim.start()

    # expose fadeValue property for entrance
    def getFade(self):
        return self.fade_opacity

    def setFade(self, v):
        self.fade_opacity = v
        self.update()

    def getTextFade(self):
        return getattr(self, "_text_fade", 0.0)

    def setTextFade(self, v):
        self._text_fade = v
        self.update()

    fadeValue = Property(float, getFade, setFade)
    textFade = Property(float, getTextFade, setTextFade)

    # --------------------------
    # Painting: card glass + neon accents
    # --------------------------
    def paintEvent(self, ev):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w, h = self.width(), self.height()

        # global fade overlay (entrance)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 0))

        # Draw an ambient top-left neon streak for drama
        streak = QLinearGradient(0, 0, w * 0.6, 0)
        streak.setColorAt(0.0, QColor(80, 0, 120, int(80 * self.fade_opacity)))
        streak.setColorAt(1.0, QColor(0, 180, 255, int(0 * self.fade_opacity)))
        painter.fillRect(0, 0, int(w * 0.7), int(h * 0.25), streak)

        # Draw card (glass) rectangle with subtle border and gradient
        if hasattr(self, "card"):
            cr = self.card.geometry()
            # glass background
            path = QPainterPath()
            path.addRoundedRect(QRectF(cr), 18.0, 18.0)

            # glass fill: semi-transparent, slight gradient
            g = QLinearGradient(cr.topLeft(), cr.bottomRight())
            g.setColorAt(0.0, QColor(255, 255, 255, int(18 * self.fade_opacity)))
            g.setColorAt(1.0, QColor(255, 255, 255, int(10 * self.fade_opacity)))
            painter.setBrush(g)
            painter.setPen(Qt.NoPen)
            painter.drawPath(path)

            # inner neon rim
            pen = QPen(QColor(60, 160, 255, int(170 * self.fade_opacity)))
            pen.setWidthF(1.3)
            painter.setPen(pen)
            painter.drawPath(path)

            # grab a small area for neon glow behind the icon
            icon_center = QPointF(cr.left() + 120, cr.center().y())
            glow = QRadialGradient(icon_center, 220)
            glow.setColorAt(0.0, QColor(0, 190, 255, int(120 * self.fade_opacity)))
            glow.setColorAt(0.35, QColor(180, 90, 255, int(80 * self.fade_opacity)))
            glow.setColorAt(1.0, QColor(0, 0, 0, 0))
            painter.setBrush(glow)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(icon_center, 220, 120)

        # Let child widgets paint themselves (icon, labels, CTA)
        super().paintEvent(ev)

    # --------------------------
    # draw child text with fade controlling alpha
    # --------------------------
    def drawChildren(self):
        # Not used, labels are widgets themselves; but we'll set their foreground colors depending on textFade
        alpha = int(255 * getattr(self, "_text_fade", 1.0))
        # title
        col = QColor(255, 255, 255, alpha)
        self.title_label.setStyleSheet(f"color: rgba({col.red()},{col.green()},{col.blue()},{col.alpha()})")
        self.tagline_label.setStyleSheet(f"color: rgba(220,220,255,{alpha})")
        desc_alpha = max(120, alpha)
        self.desc_label.setStyleSheet(f"color: rgba(220,220,230,{desc_alpha})")
        self.version_label.setStyleSheet("color: rgba(200,200,200,180)")
        # CTA styling - we do a simple painted background via palette: use stylesheet here only for color strings
        # (kept minimal)
        self.cta.setStyleSheet(
            "QPushButton {"
            "border-radius: 8px; padding: 8px 14px; font-weight:600;"
            f"background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(66, 170, 255, {alpha}), stop:1 rgba(150, 110, 255, {alpha}));"
            "color: white;}"
            "QPushButton:pressed { transform: translateY(1px); }"
        )

    def showEvent(self, ev):
        # start animations when shown
        self._entrance_anim.start()
        # ensure child text style updated
        self._text_anim = getattr(self, "_text_anim", None)
        self.drawChildren()
        super().showEvent(ev)


# -------------------------
# Demo / standalone run
# -------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("ImpressiveHero Demo")

    description = (
        "A playground of vibrant tools and cinematic motion —\n"
        "built to spark creativity and make workflows delightful."
    )

    hero = ImpressiveHero(
        app_name="Luminous Studio",
        tagline="Vivid tools. Joyful creation.",
        version="5.2.0",
        description=description,
        svg_data=None  # pass your SVG string here if you have one
    )
    hero.resize(1200, 560)
    hero.show()
    sys.exit(app.exec())
    