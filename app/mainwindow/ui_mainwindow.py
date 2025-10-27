# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindowVncFjC.ui'
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
    QSizePolicy, QStatusBar, QTabWidget, QVBoxLayout,
    QWidget)

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
        self.label = QLabel(self.palette_top_frame)
        self.label.setObjectName(u"label")

        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)

        self.comboBox = QComboBox(self.palette_top_frame)
        self.comboBox.setObjectName(u"comboBox")

        self.gridLayout_2.addWidget(self.comboBox, 0, 1, 1, 1)

        self.label_2 = QLabel(self.palette_top_frame)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout_2.addWidget(self.label_2, 1, 0, 1, 1)

        self.comboBox_2 = QComboBox(self.palette_top_frame)
        self.comboBox_2.setObjectName(u"comboBox_2")

        self.gridLayout_2.addWidget(self.comboBox_2, 1, 1, 1, 1)

        self.label_3 = QLabel(self.palette_top_frame)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout_2.addWidget(self.label_3, 2, 0, 1, 1)

        self.comboBox_3 = QComboBox(self.palette_top_frame)
        self.comboBox_3.setObjectName(u"comboBox_3")

        self.gridLayout_2.addWidget(self.comboBox_3, 2, 1, 1, 1)

        self.label_4 = QLabel(self.palette_top_frame)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout_2.addWidget(self.label_4, 3, 0, 1, 1)

        self.comboBox_4 = QComboBox(self.palette_top_frame)
        self.comboBox_4.setObjectName(u"comboBox_4")

        self.gridLayout_2.addWidget(self.comboBox_4, 3, 1, 1, 1)


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
        self.label.setText(QCoreApplication.translate("MainWindow", u"Accent", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Neutral", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Support", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Theme", None))
        self.mainTW.setTabText(self.mainTW.indexOf(self.palette), QCoreApplication.translate("MainWindow", u"Palette", None))
        self.mainTW.setTabText(self.mainTW.indexOf(self.fonts), QCoreApplication.translate("MainWindow", u"Fonts", None))
    # retranslateUi

