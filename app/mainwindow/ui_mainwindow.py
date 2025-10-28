# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindowNYUSkK.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QHBoxLayout,
    QLabel, QMainWindow, QMenuBar, QSizePolicy,
    QStatusBar, QTabWidget, QTextBrowser, QToolBox,
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
        self.p_frame = QFrame(self.palette)
        self.p_frame.setObjectName(u"p_frame")
        self.p_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.p_frame.setFrameShadow(QFrame.Shadow.Raised)

        self.gridLayout.addWidget(self.p_frame, 0, 0, 1, 1)

        self.gridLayout.setRowStretch(0, 3)
        self.mainTW.addTab(self.palette, "")
        self.fonts = QWidget()
        self.fonts.setObjectName(u"fonts")
        self.mainTW.addTab(self.fonts, "")
        self.settings = QWidget()
        self.settings.setObjectName(u"settings")
        self.verticalLayout_2 = QVBoxLayout(self.settings)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.settingsTB = QToolBox(self.settings)
        self.settingsTB.setObjectName(u"settingsTB")
        self.page_2 = QWidget()
        self.page_2.setObjectName(u"page_2")
        self.page_2.setGeometry(QRect(0, 0, 776, 341))
        self.settingsTB.addItem(self.page_2, u"Page 2")

        self.verticalLayout_2.addWidget(self.settingsTB)

        self.mainTW.addTab(self.settings, "")

        self.verticalLayout.addWidget(self.mainTW)

        self.log_frame = QFrame(self.centralwidget)
        self.log_frame.setObjectName(u"log_frame")
        self.log_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.log_frame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_3 = QVBoxLayout(self.log_frame)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.logTB = QTextBrowser(self.log_frame)
        self.logTB.setObjectName(u"logTB")

        self.verticalLayout_3.addWidget(self.logTB)


        self.verticalLayout.addWidget(self.log_frame)

        self.verticalLayout.setStretch(0, 1)
        self.verticalLayout.setStretch(1, 20)
        self.verticalLayout.setStretch(2, 4)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 33))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        self.mainTW.setCurrentIndex(2)
        self.settingsTB.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.titlelabel.setText(QCoreApplication.translate("MainWindow", u"Qt-Pop Demo ", None))
        self.mainTW.setTabText(self.mainTW.indexOf(self.palette), QCoreApplication.translate("MainWindow", u"Palette", None))
        self.mainTW.setTabText(self.mainTW.indexOf(self.fonts), QCoreApplication.translate("MainWindow", u"Fonts", None))
        self.settingsTB.setItemText(self.settingsTB.indexOf(self.page_2), QCoreApplication.translate("MainWindow", u"Page 2", None))
        self.mainTW.setTabText(self.mainTW.indexOf(self.settings), QCoreApplication.translate("MainWindow", u"Settings", None))
    # retranslateUi

