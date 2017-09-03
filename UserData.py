# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui, uic
from PyQt4.Qt import Qt
import metrocss

InputWindow = "datainput.ui"
Ui_InputWindow, QtBaseClass = uic.loadUiType(InputWindow)


class UserData(QtGui.QMainWindow, Ui_InputWindow):
    def __init__(self, user_data_signal, parent=None):
        
        super(UserData, self).__init__(parent)
        Ui_InputWindow.__init__(self)

        self.setupUi(self)
        self.setWindowModality(QtCore.Qt.WindowModal)
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.signal=user_data_signal
        self.label1='Температура'
        self.label2='Выдержка'
        self.tempisset=0
        self.timeisset=0
        self.T=0
        self.t=0
        self.label.setText(metrocss.SetLabelText(self.label1))
        
        
        self.b1.pressed.connect(self.setData)
        self.b2.pressed.connect(self.setData)
        self.b3.pressed.connect(self.setData)
        self.b4.pressed.connect(self.setData)
        self.b5.pressed.connect(self.setData)
        self.b6.pressed.connect(self.setData)
        self.b7.pressed.connect(self.setData)
        self.b8.pressed.connect(self.setData)
        self.b9.pressed.connect(self.setData)
        self.b0.pressed.connect(self.setData)
        self.bdel.pressed.connect(self.setData)
        self.bok.pressed.connect(self.setData)

        self.b1.released.connect(self.Clear)
        self.b2.released.connect(self.Clear)
        self.b3.released.connect(self.Clear)
        self.b4.released.connect(self.Clear)
        self.b5.released.connect(self.Clear)
        self.b6.released.connect(self.Clear)
        self.b7.released.connect(self.Clear)
        self.b8.released.connect(self.Clear)
        self.b9.released.connect(self.Clear)
        self.b0.released.connect(self.Clear)
        self.bdel.released.connect(self.Clear)
        self.bok.released.connect(self.Clear)

    def setData(self):
        sender = self.sender()
        name = sender.objectName()
        if name[1] in ('1','2','3','4','5','6','7','8','9','0') :
            point=name[1]
            point=int(point)
            sender.setStyleSheet(metrocss.data_active)
            data=self.UserData.toPlainText()
            data=int(data)
            if data==0:
                data=point
                self.UserData.setHtml(metrocss.Show_Main_Temp(data))
            else:
                data=data*10+point
                if self.tempisset==0:
                    if data>0 and data<211:
                        self.UserData.setHtml(metrocss.Show_Main_Temp(data))
                else:
                    if data>0 and data<31:
                        self.UserData.setHtml(metrocss.Show_Main_Temp(data))

        if sender==self.bdel:
            sender.setStyleSheet(metrocss.data_active)
            data=self.UserData.toPlainText()
            data=int(data)
            if data==0:
                pass
            else:
                data=data//10
                self.UserData.setHtml(metrocss.Show_Main_Temp(data))

        if sender==self.bok:
            sender.setStyleSheet(metrocss.data_active)
            if self.tempisset==0:
                self.tempisset=1
                data=self.UserData.toPlainText()
                self.T=int(data)
                self.label.setText(metrocss.SetLabelText(self.label2))
                self.UserData.setHtml(metrocss.Show_Main_Temp(0))                
            else:
                self.timeisset=1
                data=self.UserData.toPlainText()
                self.t=int(data)       
        
    def Clear(self):
        sender = self.sender()
        sender.setStyleSheet(metrocss.data_passive)
        if sender==self.bok and self.tempisset==1 and self.timeisset==1:
            self.signal.emit(self.T,self.t)
            self.close()
