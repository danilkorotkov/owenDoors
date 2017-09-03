# -*- coding: utf-8 -*-
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
#----------------settings--------------------------

a = {
    'start_prog1':1,
    'start_prog2':1,
    'OH_ctrl_1':1,
    'OH_ctrl_2':1,
    'sensor1_1':1,
    'sensor1_2':1,
    'sensor2_1':1,
    'sensor2_2':1,
    'Fan1_Allow':1,
    'Fan2_Allow':1,
    'Channel1':[3.5708,5.3255,319.73,-249.65],
    'Channel2':[3.5708,5.3255,319.73,-249.65],
    'Channel3':[3.5708,5.3255,319.73,-249.65],
    'Channel4':[3.5708,5.3255,319.73,-249.65],
    'Channel5':[3.5708,5.3255,319.73,-249.65],
    'Channel6':[3.5708,5.3255,319.73,-249.65],
    'Counter1':0,
    'Counter2':0
}

#-----------------styles---------------------------

    #-----------buttons-------------
data_active=_fromUtf8("border-style: outset;\n"
"font: 75 65pt \"HelveticaNeueCyr\";\n"
"padding: 16px;\n"
"color:black;\n"
" text-align: center;\n"
" background-color: rgb(231, 126, 35);\n"
"")

data_passive=_fromUtf8("border-style: outset;\n"
"font: 75 65pt \"HelveticaNeueCyr\";\n"
"padding: 16px;\n"
"color:black;\n"
" text-align: center;\n"
" background-color: rgb(194, 194, 194);\n"
"")

prog_active=_fromUtf8("border-style: outset;\n"
"font: 16pt \"Free Helvetian\";\n"
"color:black;\n"
" text-align: center;\n"
" background-color: rgb(231, 126, 35);\n"
"")

prog_passive=_fromUtf8("border-style: outset;\n"
"font: 16pt \"Free Helvetian\";\n"
"color:black;\n"
" text-align: center;\n"
" background-color: rgb(194, 194, 194);\n"
"")

StartButton_active=_fromUtf8("border-style: outset;\n"
"font: 18pt \"Free Helvetian\";\n"
"color:white;\n"
" font-weight: bold;\n"
" text-align: center;\n"
" background-color: rgb(63, 179, 79);")

StartButton_passive=_fromUtf8("border-style: outset;\n"
"font: 18pt \"Free Helvetian\";\n"
"color:white;\n"
" font-weight: bold;\n"
" text-align: center;\n"
" background-color:  rgb(183, 183, 183);")

StopButton_active=_fromUtf8("border-style: outset;\n"
"font: 18pt \"Free Helvetian\";\n"
"color:white;\n"
" font-weight: bold;\n"
" text-align: center;\n"
" background-color: rgb(195, 44, 27);\n"
"")

StopButton_passive=_fromUtf8("border-style: outset;\n"
"font: 18pt \"Free Helvetian\";\n"
"color:white;\n"
" font-weight: bold;\n"
" text-align: center;\n"
" background-color: rgb(183, 183, 183);\n"
"")

SetButtons_passive=_fromUtf8("border-style: outset;\n"
"font: 16pt \"Free Helvetian\";\n"
"color:black;\n"
" text-align: center;\n"
" background-color: rgb(194, 194, 194);\n"
"")
SetButtons_active=_fromUtf8("border-style: outset;\n"
"font: 16pt \"Free Helvetian\";\n"
"color:black;\n"
" text-align: center;\n"
" background-color: rgb(231, 126, 35);\n"
"")


    #---------work zone---------
MainTemp_working=_fromUtf8("border-style: outset;\n"
"padding: 16px;\n"
"color:black;\n"
"background-color: rgb(231, 126, 35);\n"
"")

MainTemp_waiting=_fromUtf8("border-style: outset;\n"
"padding: 16px;\n"
"color:black;\n"
"background-color: rgb(114, 208, 244);\n"
"")

Channel_waiting=_fromUtf8("border-style: outset;\n"
"font: 16pt \"Free Helvetian\";\n"
"padding: -7px;\n"
"color:black;\n"
"background-color: rgb(114, 208, 244);")

Channel_working=_fromUtf8("border-style: outset;\n"
"font: 16pt \"Free Helvetian\";\n"
"padding: -7px;\n"
"color:black;\n"
"background-color: rgb(231, 126, 35);")

InfoPanel_working=_fromUtf8("border-style: outset;\n"
"font: 14pt \"Free Helvetian\";\n"
"padding: -6px;\n"
"color:black;\n"
"background-color: rgb(231, 126, 35);")

InfoPanel_waiting=_fromUtf8("border-style: outset;\n"
"font: 14pt \"Free Helvetian\";\n"
"padding: -6px;\n"
"color:black;\n"
"background-color: rgb(114, 208, 244);")

Sets_waiting=_fromUtf8("border-style: outset;\n"
"font: 14pt \"Free Helvetian\";\n"
"padding: 0px;\n"
"color:black;\n"
"background-color: rgb(114, 208, 244);\n"
"")

Sets_working=_fromUtf8("border-style: outset;\n"
"font: 14pt \"Free Helvetian\";\n"
"padding: 0px;\n"
"color:black;\n"
"background-color: rgb(231, 126, 35);\n"
"")

Rate_Counter_working=_fromUtf8("border-style: outset;\n"
"font: 12pt \"Free Helvetian\";\n"
"padding: -2px;\n"
"color:black;\n"
"background-color: rgb(231, 126, 35);\n"
"")

Rate_Counter_waiting=_fromUtf8("border-style: outset;\n"
"font: 12pt \"Free Helvetian\";\n"
"padding: -2px;\n"
"color:black;\n"
"background-color: rgb(114, 208, 244);\n"
"")


#---------------------htmls---------------------
def settemp(temp):
    out=_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Free Helvetian\'; font-size:14pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Уставка: </p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"> %.1f </p></body></html>"%temp, None)
    return out

def setdelay(timedelay):
    out=_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Free Helvetian\'; font-size:14pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Выдержка: </p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"> %s:00 </p></body></html>"%timedelay, None)
    return out

def Show_temp(temp):
    out =_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Free Helvetian\'; font-size:16pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"> %s </p></body></html>"%temp, None)
    return out
def Show_Counter(count):
    out=_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Free Helvetian\'; font-size:12pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt;\">Счетчик:</span></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt;\"> %i </span></p></body></html>"%count, None)
    return out

def Show_User_Data (data):
    out=_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Free Helvetian\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'HelveticaNeueCyr\'; font-size:82pt;\"> %s </span></p></body></html>"%data, None)
    return out

def Show_Main_Temp (temp):
    out=_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Free Helvetian\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'HelveticaNeueCyr\'; font-size:78pt;\"> %s </span></p></body></html>"%temp, None)
    return out

def SetLabelText (text):
    out=_translate("MainWindow", "%s"%text, None)
    return out

def SetInfoPanelText (text):
    out=_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Free Helvetian\'; font-size:14pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Статус: %s</p></body></html>"%text, None)
    return out

def Show_Rate (text):
    out=_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Free Helvetian\'; font-size:12pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt;\">Скорость:</span></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt;\">%.1f°С/мин</span></p></body></html>"%text, None)
    return out    

def Show_err (err):
    out=_translate("MainWindow",
                                       "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
                                       "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
                                       "p, li { white-space: pre-wrap; }\n"
                                       "</style></head><body style=\" font-family:\'Free Helvetian\'; font-size:14pt; font-weight:400; font-style:normal;\">\n"
                                       "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">%s</p>\n"
                                       "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">%s</p>\n"
                                       "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">%s</p>\n"
                                       "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">%s</p>\n"
                                       "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">%s</p></body></html>" % (err[0], err[1], err[2], err[3], err[4]), None)
    return out