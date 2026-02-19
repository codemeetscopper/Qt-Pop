from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame, QLabel, QSizePolicy, QVBoxLayout, QWidget,
)


class AboutPage(QWidget):
    """Centered info card about the Nova application."""

    def __init__(self, qt_pop, parent: QWidget | None = None):
        super().__init__(parent)
        self._qt_pop = qt_pop
        self.setObjectName("AboutPage")

        outer = QVBoxLayout(self)
        outer.setAlignment(Qt.AlignCenter)
        outer.setContentsMargins(40, 40, 40, 40)

        card = QFrame()
        card.setObjectName("AboutCard")
        card.setFrameShape(QFrame.StyledPanel)
        card.setFixedWidth(480)
        card.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        v = QVBoxLayout(card)
        v.setContentsMargins(40, 40, 40, 40)
        v.setSpacing(16)
        v.setAlignment(Qt.AlignCenter)

        # App name
        name = QLabel("Nova")
        name.setObjectName("AboutAppName")
        name.setAlignment(Qt.AlignCenter)
        v.addWidget(name)

        # Version
        try:
            ver_val = qt_pop.config.get_value("version")
            ver_str = getattr(ver_val, "value", "1.0.0") if ver_val else "1.0.0"
        except Exception:
            ver_str = "1.0.0"

        version = QLabel(f"Version {ver_str}")
        version.setObjectName("AboutVersion")
        version.setAlignment(Qt.AlignCenter)
        v.addWidget(version)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setObjectName("AboutSeparator")
        v.addWidget(sep)

        desc = QLabel(
            "Nova is a futuristic, plugin-driven application platform\n"
            "built on PySide6 and the Qt-Pop theming toolkit.\n\n"
            "Each plugin runs in an isolated subprocess for\n"
            "maximum stability and security."
        )
        desc.setObjectName("AboutDescription")
        desc.setAlignment(Qt.AlignCenter)
        desc.setWordWrap(True)
        v.addWidget(desc)

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.HLine)
        sep2.setObjectName("AboutSeparator")
        v.addWidget(sep2)

        license_lbl = QLabel("License: MIT")
        license_lbl.setObjectName("AboutLicense")
        license_lbl.setAlignment(Qt.AlignCenter)
        v.addWidget(license_lbl)

        outer.addWidget(card)
