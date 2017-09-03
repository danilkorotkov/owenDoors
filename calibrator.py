# -*- coding: utf-8 -*-
import numpy
import spidev, time, csv, math
from PyQt4 import QtCore, QtGui, uic
from PyQt4.Qt import Qt
import RPi.GPIO as GPIO

MainInterfaceWindow = "calibrator.ui"
Ui_Calibrator, QtBaseClass = uic.loadUiType(MainInterfaceWindow)
# -------------GPIO---------------
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

A = 21
B = 20
C = 16

Mux = (C, B, A)
spi = spidev.SpiDev()


# --------------------ADC Thread-------------
class TempThread(QtCore.QThread):  # работа с АЦП в потоке
    def __init__(self, temp_signal, parent=None):
        super(TempThread, self).__init__(parent)
        self.temp_signal = temp_signal
        self.isRun = False
        self.Va = 0
        self.SetChannel(1)

    def run(self):
        while self.isRun:
            self.Va = self.GetADC()
            self.temp_signal.emit(self.Va)
            time.sleep(0.4)

    def stop(self):
        self.isRun = False
        time.sleep(0.5)
        spi.close()

    def GetADC(self):  # все названия сохранены на языке автора функции
        M0 = 0
        muestras = 0
        while muestras <= 49:
            adc = spi.xfer2([0, 0])
            hi = (adc[0] & 0x1F)
            low = (adc[1] & 0xFC)  # FE for B, FC for C chip (MCP3201-B/C) ©Danil
            dato = (hi << 8) | low
            M0 += dato
            muestras += 1
        dato = M0 / 50
        V = dato * 2.5 / 8192.0
        return V

    def SetChannel(self, Ch):
        if Ch >= 1 or Ch <= 6:
            A = Ch >> 2
            B = (Ch >> 1) & 1
            C = Ch & 1
            GPIO.output(Mux, (A, B, C))


class Calibrator(QtGui.QMainWindow, Ui_Calibrator):
    """Calibrator inherits QMainWindow"""
    temp_signal = QtCore.pyqtSignal(float)

    Temp = [0, 175, 266.5, 558]
    A3 = 0
    A2 = 0
    A1 = 0
    A0 = 0
    # Volts=[[value, IsSet],[value, IsSet],[value, IsSet],[value, IsSet]]
    Volts = [[0, 0], [0, 0], [0, 0], [0, 0]]
    C = 1
    R = 0
    lineCalcked = 0
    Va = 0
    isItStart = 0
    TextCoeff = ''
    TextErr1 = u'Не все ячейки записаны или калибровка не посчитана'
    TextErr2 = u'Не все ячейки записаны'
    Stored = ' '
    Coeff = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]

    def __init__(self, finish_signal, parent=None):
        super(Calibrator, self).__init__(parent)
        Ui_Calibrator.__init__(self)
        self.setupUi(self)
        self.move(315, 33)
        self.setWindowModality(QtCore.Qt.WindowModal)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.a = read_settings()
        self.Coeff = get_coeff(self.a, self.Temp)
        self.finish_signal = finish_signal

        self.set_adc()

        self.pBtn_Channel_1.setStyleSheet(CellSelect)
        self.R0.setStyleSheet(CellSelect)
        self.TextCoeff = str(self.Coeff[0])

        self.textEdit.setHtml(HtmlText(self.TextCoeff, self.Stored, ' '))

        self.R0.pressed.connect(self.RB)
        self.R1.pressed.connect(self.RB)
        self.R2.pressed.connect(self.RB)
        self.R3.pressed.connect(self.RB)

        self.pBtn_Channel_1.clicked.connect(self.changeRow)
        self.pBtn_Channel_2.clicked.connect(self.changeRow)
        self.pBtn_Channel_3.clicked.connect(self.changeRow)
        self.pBtn_Channel_4.clicked.connect(self.changeRow)
        self.pBtn_Channel_5.clicked.connect(self.changeRow)
        self.pBtn_Channel_6.clicked.connect(self.changeRow)

        self.pushButton_2.pressed.connect(self.Get_Volts)
        self.pushButton_3.pressed.connect(self.Calc)
        self.SaveButton.pressed.connect(self.save_settings)

        self.pushButton_2.released.connect(lambda: self.sender().setStyleSheet(ButPassive))
        self.pushButton_3.released.connect(lambda: self.sender().setStyleSheet(ButPassive))
        self.SaveButton.released.connect(lambda: self.sender().setStyleSheet(ButPassive))

        self.Exit.pressed.connect(self.Exit_)
        self.Exit.released.connect(self.Exit__)

    def __del__(self):
        self.ui = None

    # ----------------------methods-------------------------------
    def Exit__(self):
        self.Exit.setStyleSheet(ButPassive)
        self.close()

    def Exit_(self):
        self.textEdit.setHtml(HtmlText(' ', u'Выход...', ' '))
        self.Exit.setStyleSheet(ButActive)
        self.finish_signal.emit()

    def changeRow(self):
        sender = self.sender()
        name = sender.objectName()
        s = len(name)

        if self.isItStart == 0:

            getattr(self, 'lineEdit_' + str((self.C - 1) * 4 + self.R + 1)).setStyleSheet(CellWait)
            getattr(self, 'pBtn_Channel_' + str(self.C)).setStyleSheet(CellWait)
            self.C = int(name[s - 1])
            self.tempthread.SetChannel(self.C)
            sender.setStyleSheet(CellSelect)

            self.TextCoeff = str(self.Coeff[self.C - 1])
            self.textEdit.setHtml(HtmlText(self.TextCoeff, ' ', ' '))

            return

        elif self.checkRow() & self.lineCalcked == 0:
            self.textEdit.setHtml(HtmlText(self.TextCoeff, self.Stored, self.TextErr1))
            self.GroupChannel.checkedButton().setChecked(False)
            getattr(self, 'pBtn_Channel_' + str(self.C)).setChecked(True)

            return

        getattr(self, 'pBtn_Channel_' + str(self.C)).setStyleSheet(CellWait)
        self.C = int(name[s - 1])
        self.lineCalcked = 0
        sender.setStyleSheet(CellSelect)

        self.TextCoeff = str(self.Coeff[self.C - 1])
        self.textEdit.setHtml(HtmlText(self.TextCoeff, ' ', ' '))

    def checkRow(self):
        out = self.Volts[0][1] & self.Volts[1][1] & self.Volts[2][1] & self.Volts[3][1]
        return out

    def got_worker_msg(self, Va):  # ловля сигнала от АЦП
        self.Va = Va
        getattr(self, 'lineEdit_' + str((self.C - 1) * 4 + self.R + 1)).setText('')
        getattr(self, 'lineEdit_' + str((self.C - 1) * 4 + self.R + 1)).setText("%.4f" % self.Va)
        if not self.Volts[self.R][1]:
            getattr(self, 'lineEdit_' + str((self.C - 1) * 4 + self.R + 1)).setStyleSheet(CellSelect)

    def set_adc(self):  # запуск ацп в потоке
        GPIO.setup(Mux, GPIO.OUT)
        GPIO.output(Mux, (0, 0, 0))

        spi.open(0, 0)
        spi.max_speed_hz = 40000
        self.tempthread = TempThread(self.temp_signal)
        self.temp_signal.connect(self.got_worker_msg, QtCore.Qt.QueuedConnection)
        self.tempthread.isRun = True
        self.tempthread.start()

    def Calc(self):
        self.pushButton_3.setStyleSheet(ButActive)

        if self.checkRow() == 0:
            self.textEdit.setHtml(HtmlText(self.TextCoeff, self.Stored, self.TextErr2))
            return

        self.lineCalcked = 1
        self.isItStart = 0

        for x in range(4):
            self.Volts[x][1] = 0
        self.test1()

    def Get_Volts(self):
        self.pushButton_2.setStyleSheet(ButActive)

        self.isItStart = 1
        self.Volts[self.R][1] = True
        self.Volts[self.R][0] = float(self.Va)
        self.Stored = u'Записано ' + "%.4f" % self.Va
        self.textEdit.setHtml(HtmlText(self.TextCoeff, self.Stored, ' '))
        getattr(self, 'lineEdit_' + str((self.C - 1) * 4 + self.R + 1)).setStyleSheet(CellStored)

    def test1(self):
        self.textEdit.setText("")

        A = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        xy = [[0, 0], [0, 0], [0, 0], [0, 0]]

        xy[0][0] = self.Volts[0][0]
        xy[1][0] = self.Volts[1][0]
        xy[2][0] = self.Volts[2][0]
        xy[3][0] = self.Volts[3][0]

        xy[0][1] = self.Temp[0]
        xy[1][1] = self.Temp[1]
        xy[2][1] = self.Temp[2]
        xy[3][1] = self.Temp[3]

        a6 = 0
        a5 = 0
        a4 = 0
        a3 = 0
        a2 = 0
        a1 = 0
        a0 = 0
        b3 = 0
        b2 = 0
        b1 = 0
        b0 = 0

        for i in range(len(xy)):
            a6 += xy[i][0] ** 6
            a5 += xy[i][0] ** 5
            a4 += xy[i][0] ** 4
            a3 += xy[i][0] ** 3
            a2 += xy[i][0] ** 2
            a1 += xy[i][0]
            a0 += 1.0
            b3 += xy[i][1] * xy[i][0] ** 3
            b2 += xy[i][1] * xy[i][0] ** 2
            b1 += xy[i][1] * xy[i][0]
            b0 += xy[i][1]

        A[0][0] = a6
        A[0][1] = a5
        A[0][2] = a4
        A[0][3] = a3

        A[1][0] = a5
        A[1][1] = a4
        A[1][2] = a3
        A[1][3] = a2

        A[2][0] = a4
        A[2][1] = a3
        A[2][2] = a2
        A[2][3] = a1

        A[3][0] = a3
        A[3][1] = a2
        A[3][2] = a1
        A[3][3] = a0

        detA = numpy.linalg.det(A)
        if detA != 0.0:
            # print A

            B3 = A[:]
            B3[0][0] = b3
            B3[1][0] = b2
            B3[2][0] = b1
            B3[3][0] = b0
            # print B3
            # print A
            detB3 = numpy.linalg.det(B3)
            self.A3 = detB3 / detA
            # print A3
            B3[0][0] = a6
            B3[1][0] = a5
            B3[2][0] = a4
            B3[3][0] = a3
            B2 = A[:]
            B2[0][1] = b3
            B2[1][1] = b2
            B2[2][1] = b1
            B2[3][1] = b0
            detB2 = numpy.linalg.det(B2)
            self.A2 = detB2 / detA
            # print A2
            B2[0][1] = a5
            B2[1][1] = a4
            B2[2][1] = a3
            B2[3][1] = a2
            B1 = A[:]
            B1[0][2] = b3
            B1[1][2] = b2
            B1[2][2] = b1
            B1[3][2] = b0
            detB1 = numpy.linalg.det(B1)
            self.A1 = detB1 / detA
            # print A1
            B1[0][2] = a4
            B1[1][2] = a3
            B1[2][2] = a2
            B1[3][2] = a1
            B0 = A[:]
            B0[0][3] = b3
            B0[1][3] = b2
            B0[2][3] = b1
            B0[3][3] = b0
            detB0 = numpy.linalg.det(B0)
            self.A0 = detB0 / detA
            # print A0

            Chann = 'Channel' + str(self.C)
            self.a[Chann][0] = round(self.A3, 4)
            self.a[Chann][1] = round(self.A2, 4)
            self.a[Chann][2] = round(self.A1, 4)
            self.a[Chann][3] = round(self.A0, 4)

            eq = ("%.4fx" % self.A3 + u'\xB3' + self.sign(self.A2) + \
                  "%.4fx" % abs(self.A2) + u'\xB2' + self.sign(self.A1) + \
                  "%.4fx" % abs(self.A1) + self.sign(self.A0) + \
                  "%.4f" % abs(self.A0))
            self.textEdit.setHtml(HtmlText(self.TextCoeff, eq, ''))
        else:
            self.textEdit.setHtml(HtmlText(self.TextCoeff, ' ', 'detA=0'))

        getattr(self, 'lineEdit_' + str((self.C - 1) * 4 + 0 + 1)).setStyleSheet(CellWait)
        getattr(self, 'lineEdit_' + str((self.C - 1) * 4 + 1 + 1)).setStyleSheet(CellWait)
        getattr(self, 'lineEdit_' + str((self.C - 1) * 4 + 2 + 1)).setStyleSheet(CellWait)
        getattr(self, 'lineEdit_' + str((self.C - 1) * 4 + 3 + 1)).setStyleSheet(CellWait)

    def sign(self, tempor):
        if tempor >= 0:
            out = '+'
        else:
            out = '-'
        return out

    def RB(self):
        sender = self.sender()
        name = sender.objectName()
        s = len(name)
        sender.setStyleSheet(CellSelect)
        getattr(self, 'R' + str(self.R)).setStyleSheet(CellWait)
        if not self.Volts[self.R][1]:
            getattr(self, 'lineEdit_' + str((self.C - 1) * 4 + self.R + 1)).setStyleSheet(CellWait)

        self.R = int(name[s - 1])

    def save_settings(self):
        sets = self.a
        self.SaveButton.setStyleSheet(ButActive)

        with open('settings.txt', 'wt') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter='=',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for key, val in sets.items():
                spamwriter.writerow([key, val])
        self.textEdit.setHtml(HtmlText(self.TextCoeff, ' ', u'Калибровки сохранены в файл'))


# ------------------------Globals---------------------------------------------
def get_coeff(sets, Temp):
    coeff = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    for Ch in range(1, 7):
        for i in range(4):
            a = sets['Channel' + str(Ch)][1] / sets['Channel' + str(Ch)][0]
            b = sets['Channel' + str(Ch)][2] / sets['Channel' + str(Ch)][0]
            c = (sets['Channel' + str(Ch)][3] - Temp[i]) / sets['Channel' + str(Ch)][0]
            q = (a * a - 3 * b) / 9
            r = (a * (2 * a * a - 9 * b) + 27 * c) / 54
            r2 = r * r
            q3 = q * q * q
            t = math.asinh(abs(r) / math.sqrt(abs(q3))) / 3
            y = -2 * math.sinh(t) * math.sqrt(abs(-q)) * numpy.sign(r) - a / 3
            coeff[Ch - 1][i] = float("%.4f" % y)
    return coeff


def read_settings():
    sets={}
    try:
        with open('settings.txt', 'rt') as csvfile:
            spamreader = csv.reader(csvfile, delimiter='=', quotechar='|')
            for row in spamreader:
                k, v = row
                try:
                    sets[k] = int(v)
                except ValueError:
                    line = v
                    line = line.replace('[', '')
                    line = line.replace(']', '')
                    sets[k] = line.split(",")
                    s = len(sets[k])
                    i = 0
                    while i < s:
                        x = sets[k][i]
                        x = float(x)
                        sets[k][i] = x
                        i += 1
    except IOError:
        sets = metrocss.a
        save_settings(sets)
    return sets


# ---------------------------StyleSheet---------------------------------------
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

CellWait = _fromUtf8("font: 22pt \"HelveticaNeueCyr\";\n"
                     "background-color: rgb(114, 208, 244);")

CellSelect = _fromUtf8("font: 22pt \"HelveticaNeueCyr\";\n"
                       "background-color: rgb(231, 126, 35);")

CellStored = _fromUtf8("font: 22pt \"HelveticaNeueCyr\";\n"
                       "background-color: rgb(63, 179, 79);")


def HtmlText(s1, s2, s3):
    out = _translate("MainWindow",
                     "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
                     "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
                     "p, li { white-space: pre-wrap; }\n"
                     "</style></head><body style=\" font-family:\'HelveticaNeueCyr\'; font-size:28pt; font-weight:400; font-style:normal;\">\n"
                     "<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">%s</p>\n"
                     "<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">%s</p>\n"
                     "<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">%s</p></body></html>" % (
                     s1, s2, s3), None)
    return out


ButPassive = _fromUtf8("border-style: outset;\n"
                       "font: 18pt \"HelveticaNeueCyr\";\n"
                       "color:black;\n"
                       " text-align: center;\n"
                       " background-color: rgb(194, 194, 194);\n"
                       "")

ButActive = _fromUtf8("border-style: outset;\n"
                      "font: 18pt \"HelveticaNeueCyr\";\n"
                      "color:black;\n"
                      " text-align: center;\n"
                      " background-color: rgb(231, 126, 35);\n"
                      "")
