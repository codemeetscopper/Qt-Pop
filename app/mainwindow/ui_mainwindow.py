# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindowviUrwP.ui'
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
    QListWidget, QListWidgetItem, QMainWindow, QMenuBar,
    QPushButton, QSizePolicy, QStatusBar, QTabWidget,
    QTextEdit, QToolBox, QVBoxLayout, QWidget)

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
        self.mainTW = QTabWidget(self.centralwidget)
        self.mainTW.setObjectName(u"mainTW")
        self.home = QWidget()
        self.home.setObjectName(u"home")
        self.mainTW.addTab(self.home, "")
        self.settings = QWidget()
        self.settings.setObjectName(u"settings")
        self.verticalLayout_2 = QVBoxLayout(self.settings)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.settingsTB = QToolBox(self.settings)
        self.settingsTB.setObjectName(u"settingsTB")
        self.page_2 = QWidget()
        self.page_2.setObjectName(u"page_2")
        self.page_2.setGeometry(QRect(0, 0, 776, 439))
        self.settingsTB.addItem(self.page_2, u"Page 2")

        self.verticalLayout_2.addWidget(self.settingsTB)

        self.saveBtn = QPushButton(self.settings)
        self.saveBtn.setObjectName(u"saveBtn")

        self.verticalLayout_2.addWidget(self.saveBtn, 0, Qt.AlignmentFlag.AlignRight)

        self.mainTW.addTab(self.settings, "")
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
        self.qss = QWidget()
        self.qss.setObjectName(u"qss")
        self.verticalLayout_4 = QVBoxLayout(self.qss)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.frame = QFrame(self.qss)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.frame)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.cqss = QTextEdit(self.frame)
        self.cqss.setObjectName(u"cqss")

        self.horizontalLayout_2.addWidget(self.cqss)

        self.tqss = QTextEdit(self.frame)
        self.tqss.setObjectName(u"tqss")

        self.horizontalLayout_2.addWidget(self.tqss)


        self.verticalLayout_4.addWidget(self.frame)

        self.loadbtn = QPushButton(self.qss)
        self.loadbtn.setObjectName(u"loadbtn")

        self.verticalLayout_4.addWidget(self.loadbtn, 0, Qt.AlignmentFlag.AlignRight)

        self.applybtn = QPushButton(self.qss)
        self.applybtn.setObjectName(u"applybtn")
        self.applybtn.setFlat(True)

        self.verticalLayout_4.addWidget(self.applybtn, 0, Qt.AlignmentFlag.AlignRight)

        self.verticalLayout_4.setStretch(0, 20)
        self.verticalLayout_4.setStretch(2, 1)
        self.mainTW.addTab(self.qss, "")
        self.fonts = QWidget()
        self.fonts.setObjectName(u"fonts")
        self.verticalLayout_5 = QVBoxLayout(self.fonts)
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.font_bottom = QFrame(self.fonts)
        self.font_bottom.setObjectName(u"font_bottom")
        self.font_bottom.setFrameShape(QFrame.Shape.StyledPanel)
        self.font_bottom.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_6 = QVBoxLayout(self.font_bottom)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.fontLW = QListWidget(self.font_bottom)
        self.fontLW.setObjectName(u"fontLW")

        self.verticalLayout_6.addWidget(self.fontLW)


        self.verticalLayout_5.addWidget(self.font_bottom)

        self.verticalLayout_5.setStretch(0, 10)
        self.mainTW.addTab(self.fonts, "")
        self.log = QWidget()
        self.log.setObjectName(u"log")
        self.verticalLayout_7 = QVBoxLayout(self.log)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.mainTW.addTab(self.log, "")

        self.verticalLayout.addWidget(self.mainTW)

        self.verticalLayout.setStretch(0, 20)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 33))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        self.mainTW.setCurrentIndex(5)
        self.settingsTB.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.mainTW.setTabText(self.mainTW.indexOf(self.home), QCoreApplication.translate("MainWindow", u"Home", None))
        self.settingsTB.setItemText(self.settingsTB.indexOf(self.page_2), QCoreApplication.translate("MainWindow", u"Page 2", None))
        self.saveBtn.setText(QCoreApplication.translate("MainWindow", u"Save", None))
        self.mainTW.setTabText(self.mainTW.indexOf(self.settings), QCoreApplication.translate("MainWindow", u"Settings", None))
        self.mainTW.setTabText(self.mainTW.indexOf(self.palette), QCoreApplication.translate("MainWindow", u"Palette", None))
        self.loadbtn.setText(QCoreApplication.translate("MainWindow", u"load Qss", None))
        self.applybtn.setText(QCoreApplication.translate("MainWindow", u"Apply", None))
        self.mainTW.setTabText(self.mainTW.indexOf(self.qss), QCoreApplication.translate("MainWindow", u"Qss Editor", None))
        self.mainTW.setTabText(self.mainTW.indexOf(self.fonts), QCoreApplication.translate("MainWindow", u"Fonts", None))
        self.mainTW.setTabText(self.mainTW.indexOf(self.log), QCoreApplication.translate("MainWindow", u"Logging", None))
    # retranslateUi

