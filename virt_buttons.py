# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'virt_buttons.ui'
#
# Created: Fri Mar 31 21:46:58 2017
#      by: PyQt4 UI code generator 4.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(1280, 1024)
        MainWindow.setStyleSheet(_fromUtf8(""))
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.StartButton1 = QtGui.QPushButton(self.centralwidget)
        self.StartButton1.setGeometry(QtCore.QRect(15, 75, 134, 139))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.StartButton1.sizePolicy().hasHeightForWidth())
        self.StartButton1.setSizePolicy(sizePolicy)
        self.StartButton1.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.StartButton1.setFocusPolicy(QtCore.Qt.NoFocus)
        self.StartButton1.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.StartButton1.setAcceptDrops(False)
        self.StartButton1.setStyleSheet(_fromUtf8("border-style: outset;\n"
"background-color: none;\n"
""))
        self.StartButton1.setText(_fromUtf8(""))
        self.StartButton1.setAutoRepeat(False)
        self.StartButton1.setAutoRepeatDelay(1000)
        self.StartButton1.setAutoRepeatInterval(2000)
        self.StartButton1.setObjectName(_fromUtf8("StartButton1"))
        self.StopButton1 = QtGui.QPushButton(self.centralwidget)
        self.StopButton1.setGeometry(QtCore.QRect(15, 227, 134, 139))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.StopButton1.sizePolicy().hasHeightForWidth())
        self.StopButton1.setSizePolicy(sizePolicy)
        self.StopButton1.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.StopButton1.setFocusPolicy(QtCore.Qt.NoFocus)
        self.StopButton1.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.StopButton1.setAcceptDrops(False)
        self.StopButton1.setStyleSheet(_fromUtf8("border-style: outset;\n"
"background-color: none;\n"
""))
        self.StopButton1.setText(_fromUtf8(""))
        self.StopButton1.setAutoRepeat(False)
        self.StopButton1.setAutoRepeatDelay(1000)
        self.StopButton1.setAutoRepeatInterval(2000)
        self.StopButton1.setObjectName(_fromUtf8("StopButton1"))
        self.StopButton2 = QtGui.QPushButton(self.centralwidget)
        self.StopButton2.setGeometry(QtCore.QRect(651, 227, 134, 139))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.StopButton2.sizePolicy().hasHeightForWidth())
        self.StopButton2.setSizePolicy(sizePolicy)
        self.StopButton2.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.StopButton2.setFocusPolicy(QtCore.Qt.NoFocus)
        self.StopButton2.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.StopButton2.setAcceptDrops(False)
        self.StopButton2.setStyleSheet(_fromUtf8("border-style: outset;\n"
"background-color: none;\n"
""))
        self.StopButton2.setText(_fromUtf8(""))
        self.StopButton2.setAutoRepeat(False)
        self.StopButton2.setAutoRepeatDelay(1000)
        self.StopButton2.setAutoRepeatInterval(2000)
        self.StopButton2.setObjectName(_fromUtf8("StopButton2"))
        self.StartButton2 = QtGui.QPushButton(self.centralwidget)
        self.StartButton2.setGeometry(QtCore.QRect(651, 75, 134, 139))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.StartButton2.sizePolicy().hasHeightForWidth())
        self.StartButton2.setSizePolicy(sizePolicy)
        self.StartButton2.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.StartButton2.setFocusPolicy(QtCore.Qt.NoFocus)
        self.StartButton2.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.StartButton2.setAcceptDrops(False)
        self.StartButton2.setStyleSheet(_fromUtf8("border-style: outset;\n"
"background-color: none;\n"
""))
        self.StartButton2.setText(_fromUtf8(""))
        self.StartButton2.setAutoRepeat(False)
        self.StartButton2.setAutoRepeatDelay(1000)
        self.StartButton2.setAutoRepeatInterval(2000)
        self.StartButton2.setObjectName(_fromUtf8("StartButton2"))
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "МетроКонтроль", None))

