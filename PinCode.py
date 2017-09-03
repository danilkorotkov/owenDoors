# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui, uic
from PyQt4.Qt import Qt
import metrocss

InputWindow = "datainput.ui"
Ui_InputWindow, QtBaseClass = uic.loadUiType(InputWindow)

class PinCode(QtGui.QMainWindow, Ui_InputWindow):
    def __init__(self, user_data_signal, parent=None):
        
        super(PinCode, self).__init__(parent)
        Ui_InputWindow.__init__(self)

        self.setupUi(self)
        self.setWindowModality(QtCore.Qt.WindowModal)
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.signal=user_data_signal
        self.label1=u'ПИНКОД'
        self.data=''
        self.UserData.setHtml(metrocss.Show_Main_Temp(''))

        self.label.setText(metrocss.SetLabelText(self.label1))
        self.label.setAlignment(Qt.AlignCenter)
        
        
        
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
        d=u'\xB7'
        sender = self.sender()
        name = sender.objectName()
        if name[1] in ('1','2','3','4','5','6','7','8','9','0') :
            point=name[1]
            sender.setStyleSheet(metrocss.data_active)
            self.data=self.data+point
            self.UserData.setHtml(metrocss.Show_Main_Temp(d*len(self.data)))


        if sender==self.bdel:
            sender.setStyleSheet(metrocss.data_active)

            if len(self.data)==0:
                pass
            else:
                self.data=self.data[0:-1]
                self.UserData.setHtml(metrocss.Show_Main_Temp(d*len(self.data)))


        if sender==self.bok:
            sender.setStyleSheet(metrocss.data_active)    
        
    def Clear(self):
        sender = self.sender()
        sender.setStyleSheet(metrocss.data_passive)
        if sender==self.bok:
            self.signal.emit(self.data)
            self.close()
