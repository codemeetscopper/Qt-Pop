import sys

from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtGui import QPainter, QColor, QPen, Qt
from PySide6.QtCore import QTimer, QEasingCurve, QPropertyAnimation, QParallelAnimationGroup, QRectF, QPointF, \
    QSequentialAnimationGroup


class FaceWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(640, 800)  # match screen resolution (adjust if needed)
        self.current_emotion = "neutral"
        # Default facial parameters
        self.eye_open = 1.0    # 1.0 = fully open, 0.0 = closed
        self.pupil_dx = 0.0    # horizontal offset of pupils (relative to center)
        self.pupil_dy = 0.0    # vertical offset of pupils
        self.mouth_curve = 0.0 # positive = smile, negative = frown, 0 = flat
        # Orientation (degrees)
        self.yaw = 0.0
        self.pitch = 0.0
        self.roll = 0.0
        # (Load images if any, e.g., self.mouth_images = {...})
        # Timer for blinking
        self.blink_timer = QTimer(self)
        self.blink_timer.timeout.connect(self._do_blink)
        self.blink_timer.start(3000)  # blink roughly every 3 seconds (we can randomize interval)
    def set_emotion(self, emotion_name: str):
        """Change the face to the given emotion with animation."""
        # Define target parameters for each emotion
        targets = {
            "happy":  {"eye_open": 1.0, "mouth_curve": 1.0},   # open eyes, big smile
            "sad":    {"eye_open": 0.5, "mouth_curve": -1.0},  # half-open eyes, frown
            "surprise": {"eye_open": 1.0, "mouth_curve": 0.0}, # open eyes, O-mouth (mouth_curve could be 0 used differently)
            "sleepy": {"eye_open": 0.2, "mouth_curve": -0.2},  # mostly closed eyes, slight frown
            "neutral": {"eye_open": 1.0, "mouth_curve": 0.0}
            # ... etc for other emotions
        }
        if emotion_name not in targets:
            emotion_name = "neutral"
        params = targets[emotion_name]
        # Use animations to interpolate current values to target values
        group = QParallelAnimationGroup(self)
        for param, target_value in params.items():
            # create a QPropertyAnimation for each param (assume we exposed them as Qt properties)
            anim = QPropertyAnimation(self, bytes(param, 'utf-8'))  # this is conceptual; proper PySide binding needed
            anim.setEndValue(target_value)
            anim.setDuration(300)
            anim.setEasingCurve(QEasingCurve.InOutQuad)
            group.addAnimation(anim)
        group.start()
        self.current_emotion = emotion_name
    def set_orientation(self, yaw: float, pitch: float, roll: float):
        """Update orientation angles (in degrees) and redraw the face."""
        self.yaw = yaw
        self.pitch = pitch
        self.roll = roll
        self.update()  # trigger paintEvent
    def _do_blink(self):
        """Internal: trigger a blink animation."""
        # Simple blink: close and open eyes quickly
        blink_anim = QPropertyAnimation(self, b"eye_open")
        blink_anim.setDuration(150)
        blink_anim.setStartValue(1.0)
        blink_anim.setEndValue(0.0)
        blink_anim.setEasingCurve(QEasingCurve.InOutQuad)
        # after closed, reopen
        blink_back = QPropertyAnimation(self, b"eye_open")
        blink_back.setDuration(150)
        blink_back.setStartValue(0.0)
        blink_back.setEndValue(1.0)
        blink_group = QSequentialAnimationGroup(self)
        blink_group.addAnimation(blink_anim)
        blink_group.addAnimation(blink_back)
        blink_group.start()
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        # Fill background
        painter.fillRect(self.rect(), QColor(0, 0, 0))
        # Save state and apply roll rotation
        painter.save()
        if self.roll:
            cx, cy = self.width()/2, self.height()/2
            painter.translate(cx, cy)
            painter.rotate(self.roll)  # rotate by roll degrees
            painter.translate(-cx, -cy)
        # Calculate eye positions and pupil offsets
        cx, cy = self.width()/2, self.height()/3  # center eyes around 1/3 from top
        eye_spacing = 100  # half-distance between eyes
        left_eye_center = (cx - eye_spacing, cy)
        right_eye_center = (cx + eye_spacing, cy)
        # Map yaw/pitch to pixel offsets (simple scaling)
        px = self.width() * 0.01 * self.yaw   # adjust 0.01 as needed for sensitivity
        py = self.height() * 0.01 * self.pitch
        # Draw left eye
        self._draw_eye(painter, left_eye_center, px, py)
        # Draw right eye
        self._draw_eye(painter, right_eye_center, px, py)
        # Draw mouth
        self._draw_mouth(painter, (cx, cy + 150))
        painter.restore()
    def _draw_eye(self, painter, center, pupil_offset_x, pupil_offset_y):
        x, y = center
        eye_radius = 50  # base radius
        # Eye white (or colored base)
        painter.setBrush(QColor(255, 255, 255))  # white eye
        painter.setPen(Qt.NoPen)
        # If eye_open < 1, we might scale the height to simulate closing
        h_scale = self.eye_open  # 1 = full height, 0 = closed
        rect = QRectF(x - eye_radius, y - eye_radius*h_scale, 2*eye_radius, 2*eye_radius*h_scale)
        painter.drawEllipse(rect)
        # Iris & pupil
        px = pupil_offset_x  # (in a real code, ensure px,py are within some max)
        py = pupil_offset_y
        iris_r = 20  # iris radius
        painter.setBrush(QColor(0, 170, 255))  # e.g., bright cyan iris
        painter.drawEllipse(QPointF(x + px, y + py), iris_r, iris_r)
        painter.setBrush(QColor(0, 0, 0))
        painter.drawEllipse(QPointF(x + px, y + py), iris_r/2, iris_r/2)
        # Optional: highlight
        painter.setBrush(QColor(255,255,255, 180))  # semi-transparent white
        painter.drawEllipse(QPointF(x + px - 5, y + py - 5), 3, 3)
    def _draw_mouth(self, painter, center):
        x, y = center
        width = 100
        painter.setPen(QPen(QColor(255,255,255), 8, Qt.RoundCap))
        if self.mouth_curve >= 0:
            # smile or neutral
            start_angle = 0
            span_angle = 180  # half circle
            rect = QRectF(x - width/2, y - width/2, width, width)
            painter.drawArc(rect, 0, span_angle * 16 * self.mouth_curve)  # using mouth_curve as factor
        else:
            # frown (invert arc)
            rect = QRectF(x - width/2, y - width/2, width, width)
            painter.drawArc(rect, 180*16, (-180 * self.mouth_curve) * 16)
        # For simplicity, this draws an arc; a more sophisticated approach could use QPainterPath


app = QApplication(sys.argv)
face = FaceWidget()
face.show()  # or face.showFullScreen() if using the dedicated robot screen
# Example usage:
face.set_emotion("happy")             # Show a happy face
face.set_orientation(0, 0, 0)         # Looking straight ahead
...
face.set_emotion("surprise")          # Show surprise
...
# Suppose we have IMU data for orientation:
yaw, pitch, roll = get_head_orientation()  # from sensors
face.set_orientation(yaw, pitch, roll)    # face responds to head movement
...
# Running in event loop:
sys.exit(app.exec())
