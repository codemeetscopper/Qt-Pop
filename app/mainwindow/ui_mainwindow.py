# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindowwAtnow.ui'
##
## Created by: Qt User Interface Compiler version 6.9.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QFrame, QGridLayout,
    QHBoxLayout, QLabel, QMainWindow, QMenuBar,
    QPushButton, QSizePolicy, QStatusBar, QTabWidget,
    QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setSpacing(4)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.headerframe = QFrame(self.centralwidget)
        self.headerframe.setObjectName(u"headerframe")
        self.headerframe.setFrameShape(QFrame.Shape.StyledPanel)
        self.headerframe.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout = QHBoxLayout(self.headerframe)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.titlelabel = QLabel(self.headerframe)
        self.titlelabel.setObjectName(u"titlelabel")

        self.horizontalLayout.addWidget(self.titlelabel)


        self.verticalLayout.addWidget(self.headerframe)

        self.mainTW = QTabWidget(self.centralwidget)
        self.mainTW.setObjectName(u"mainTW")
        self.palette = QWidget()
        self.palette.setObjectName(u"palette")
        self.gridLayout = QGridLayout(self.palette)
        self.gridLayout.setSpacing(5)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.palette_bottom_frame = QFrame(self.palette)
        self.palette_bottom_frame.setObjectName(u"palette_bottom_frame")
        self.palette_bottom_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.palette_bottom_frame.setFrameShadow(QFrame.Shadow.Raised)

        self.gridLayout.addWidget(self.palette_bottom_frame, 1, 0, 1, 1)

        self.palette_top_frame = QFrame(self.palette)
        self.palette_top_frame.setObjectName(u"palette_top_frame")
        self.palette_top_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.palette_top_frame.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout_2 = QGridLayout(self.palette_top_frame)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setVerticalSpacing(2)
        self.sl1 = QLabel(self.palette_top_frame)
        self.sl1.setObjectName(u"sl1")

        self.gridLayout_2.addWidget(self.sl1, 0, 0, 1, 1)

        self.accent_combo = QComboBox(self.palette_top_frame)
        self.accent_combo.setObjectName(u"accent_combo")

        self.gridLayout_2.addWidget(self.accent_combo, 0, 1, 1, 1)

        self.accent_pick = QPushButton(self.palette_top_frame)
        self.accent_pick.setObjectName(u"accent_pick")

        self.gridLayout_2.addWidget(self.accent_pick, 0, 2, 1, 1)

        self.sl2 = QLabel(self.palette_top_frame)
        self.sl2.setObjectName(u"sl2")

        self.gridLayout_2.addWidget(self.sl2, 1, 0, 1, 1)

        self.neutral_combo = QComboBox(self.palette_top_frame)
        self.neutral_combo.setObjectName(u"neutral_combo")

        self.gridLayout_2.addWidget(self.neutral_combo, 1, 1, 1, 1)

        self.neutral_pick = QPushButton(self.palette_top_frame)
        self.neutral_pick.setObjectName(u"neutral_pick")

        self.gridLayout_2.addWidget(self.neutral_pick, 1, 2, 1, 1)

        self.sl3 = QLabel(self.palette_top_frame)
        self.sl3.setObjectName(u"sl3")

        self.gridLayout_2.addWidget(self.sl3, 2, 0, 1, 1)

        self.support_combo = QComboBox(self.palette_top_frame)
        self.support_combo.setObjectName(u"support_combo")

        self.gridLayout_2.addWidget(self.support_combo, 2, 1, 1, 1)

        self.support_pick = QPushButton(self.palette_top_frame)
        self.support_pick.setObjectName(u"support_pick")

        self.gridLayout_2.addWidget(self.support_pick, 2, 2, 1, 1)

        self.sl4 = QLabel(self.palette_top_frame)
        self.sl4.setObjectName(u"sl4")

        self.gridLayout_2.addWidget(self.sl4, 3, 0, 1, 1)

        self.theme_combo = QComboBox(self.palette_top_frame)
        self.theme_combo.setObjectName(u"theme_combo")

        self.gridLayout_2.addWidget(self.theme_combo, 3, 1, 1, 1)

        self.gridLayout_2.setColumnStretch(0, 10)
        self.gridLayout_2.setColumnStretch(1, 5)
        self.gridLayout_2.setColumnStretch(2, 2)

        self.gridLayout.addWidget(self.palette_top_frame, 0, 0, 1, 1)

        self.gridLayout.setRowStretch(0, 3)
        self.gridLayout.setRowStretch(1, 7)
        self.mainTW.addTab(self.palette, "")
        self.fonts = QWidget()
        self.fonts.setObjectName(u"fonts")
        self.mainTW.addTab(self.fonts, "")

        self.verticalLayout.addWidget(self.mainTW)

        self.verticalLayout.setStretch(0, 1)
        self.verticalLayout.setStretch(1, 20)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 33))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        self.mainTW.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.titlelabel.setText(QCoreApplication.translate("MainWindow", u"Qt-Pop Demo ", None))
        self.sl1.setText(QCoreApplication.translate("MainWindow", u"Accent", None))
        self.accent_pick.setText(QCoreApplication.translate("MainWindow", u"Pick", None))
        self.sl2.setText(QCoreApplication.translate("MainWindow", u"Neutral", None))
        self.neutral_pick.setText(QCoreApplication.translate("MainWindow", u"Pick", None))
        self.sl3.setText(QCoreApplication.translate("MainWindow", u"Support", None))
        self.support_pick.setText(QCoreApplication.translate("MainWindow", u"Pick", None))
        self.sl4.setText(QCoreApplication.translate("MainWindow", u"Theme", None))
        self.mainTW.setTabText(self.mainTW.indexOf(self.palette), QCoreApplication.translate("MainWindow", u"Palette", None))
        self.mainTW.setTabText(self.mainTW.indexOf(self.fonts), QCoreApplication.translate("MainWindow", u"Fonts", None))
    # retranslateUi

