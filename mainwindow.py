# -*- coding: utf-8 -*-
import  time, csv, datetime
import minimalmodbus, sys#, string
minimalmodbus.CLOSE_PORT_AFTER_EACH_CALL = True
minimalmodbus.TIMEOUT = 0.07
from PyQt4 import QtCore, QtGui, uic
from PyQt4.Qt import Qt
from PyQt4.QtGui import *
from PyQt4.QtCore import pyqtSlot, QObject, SIGNAL
import numpy as np

#-----------------owen protocol-------------------------
from TOwen import Owen
from TSystem import MySerial

# -------------------user classes----------------------------
import metrocss
from UserData import UserData
from LongButton import LongButton, LockThread
from graphwindow import GraphWindow
from timelabel import TimeThread

# -------------------window forms----------------------------
MainInterfaceWindow = "metro_uic.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(MainInterfaceWindow)

# ---------------globals--------------------------------
reload(sys)  
sys.setdefaultencoding('utf-8')

DEGREE = u"\u00B0" + 'C'

portName = '/dev/ttyUSB0'
baudRate = 57600

pwmPeriodReg = 32
Cont1 = 1
Fan1 = 2
SSRPwm0 = 0 #owen MU offset
portTuple = (u'ТТР линии',
             u'Вентилятор  линии',
             u'Контактор  линии'
             u'Нет подключения',
             u'Нет подключения',
             u'Нет подключения',
             u'Нет подключения',
             u'Нет подключения')

Freq = 5 #pwm period
sets = {}
FI = 300 # fan interval, s
FT = 15  #fan active time, s

portIsBusy = False

mModInitStr='Modbus: '

error_buffer = ['','','','','']
def s_log(a):
    error_buffer.append(a)
    error_buffer.pop(1)

# ---------------instrument settings--------------------------------
try:
    COM = MySerial.ComPort(portName, baudRate, timeout=0.05)
except:
    raise Exception('Error openning port!')

try:
    MVA = Owen.OwenDevice(COM, 16)
    print MVA
except Owen.OwenProtocolError:
    print 'Модуль ввода отсутствует'
    s_log(u'Модуль ввода отсутствует')

try:
    MU = Owen.OwenDevice(COM, 8)
    print MU
except Owen.OwenProtocolError:
    print 'Модуль вывода отсутствует'
    s_log(u'Модуль вывода отсутствует')

MMU = minimalmodbus.Instrument(portName, slaveaddress=8, mode='rtu') # port name, slave address (in decimal)
MMU.debug = False
MMU.serial.baudrate = baudRate

try:
    if MMU.read_register(pwmPeriodReg + SSRPwm0) <> Freq:
        MMU.write_register(pwmPeriodReg + SSRPwm0, Freq)
        print 'Корректный период ШИМ'
        mModInitStr += u'Корректный период ШИМ,'
    else:
        mModInitStr += u'Корректировка ШИМ не нужна,'
except IOError:
    try:
        if MMU.read_register(pwmPeriodReg + SSRPwm0) <> Freq:
            MMU.write_register(pwmPeriodReg + SSRPwm0, Freq)
            print 'Корректный период ШИМ'
            mModInitStr += u'Корректный период ШИМ,'
        else:
            mModInitStr += u'Корректировка ШИМ не нужна,'
    except IOError:
        print 'Ошибка установки периода ШИМ'
        mModInitStr += u'Ошибка установки периода ШИМ,'

try:
    MMU.write_register(SSRPwm0, 0)
    MMU.write_register(Fan1, 0)
    MMU.write_register(Cont1, 0)
    print 'Порты в нуле'
    mModInitStr += u' Порты в нуле'
except IOError:
    try:
        MMU.write_register(SSRPwm0, 0)
        MMU.write_register(Fan1, 0)
        MMU.write_register(Cont1, 0)
        print 'Порты в нуле'
        mModInitStr += u' Порты в нуле'
    except IOError:
        print 'Ошибка установки портов'
        mModInitStr += u' Ошибка установки портов'

s_log(mModInitStr)

# --------------temp measure-----------------------
class TempThread(QtCore.QThread):  # работа с АЦП в потоке
    def __init__(self, temp_signal, parent=None):
        super(TempThread, self).__init__(parent)
        self.temp_signal = temp_signal
        self.isRun = False
        self.counter=0 # ошибки
        self.counter2=0 # операции чтения
        self.temp_array = np.array([[0.0, 0],
                                   [0.0, 0],
                                   [0.0, 0],
                                   [0.0, 0],
                                   [0.0, 0],
                                   [0.0, 0],
                                   [0.0, 0]])

    def run(self):
        global portIsBusy
        while self.isRun:
            a = datetime.datetime.now()
            s = time.localtime()
            Ch = 1
            while portIsBusy:
                print 'temp busy', portIsBusy
                time.sleep(0.05)
            while Ch <= 3:
                try:
                    portIsBusy = True
                    terr = self.temp_array[Ch][0]
                    # читаем с адреса базовый-1
                    result = MVA.GetIEEE32('rEAd', Ch-1, withTime=True)
                    print 'Ch', Ch, 'res:', result
                    self.temp_array[Ch][0] = round(result['value'],1)
                    self.temp_array[Ch][1] = int(0)
                except Owen.OwenUnpackError as e:
                    self.error_unpack(e, terr, Ch, s) # обрабатываем ошибку раскодировки данных
                except Owen.OwenProtocolError:
                    try: # пробуем еще раз
                        terr = self.temp_array[Ch][0]
                        # читаем с адреса базовый-1
                        result = MVA.GetIEEE32('rEAd', Ch - 1, withTime=True)
                        print 'Ch', Ch, 'res:', result
                        self.temp_array[Ch][0] = round(result['value'], 1)
                        self.temp_array[Ch][1] = int(0)
                    except Owen.OwenUnpackError as e:
                        self.error_unpack(e, terr, Ch, s)  # обрабатываем ошибку раскодировки данных
                    except Owen.OwenProtocolError:
                        print 'Модуль ввода не ответил, канал: ' + str(Ch)
                        s_log(u'Модуль ввода не ответил, канал: ' + str(Ch) + ' ' + str(
                                    s.tm_hour) + ':' + str(s.tm_min) + ':' + str(s.tm_sec))
                        self.counter += 1
                        if COM.isOpen():
                            COM.close()
                            COM.open()

                print self.temp_array[Ch]
                Ch+=1
            portIsBusy = False
            print '-------------------',str(s.tm_hour), ':', str(s.tm_min), ':', str(s.tm_sec), '-------------------'
            self.temp_signal.emit(self.temp_array)
            self.counter2 +=1
            error_buffer[0] = u'Ошибки = ' + str(self.counter) + u', ' + u'Вызовы = ' + str(self.counter2)
            print error_buffer[0]
            sleepparam = float(str(datetime.datetime.now() - a)[-6:]) / 1000000
            print '-------------------', sleepparam, '-------------------'
            time.sleep(5 - sleepparam)

    def stop(self):
        self.isRun = False

    def error_unpack(self, e, terr, Ch, s):
        if len(e.data) == 1:
            self.temp_array[Ch][1] = int(1)
            self.temp_array[Ch][0] = terr
            # это код ошибки
            if ord(e.data[0]) == 0xfd:
                print 'Обрыв датчика'
                s_log(u'Обрыв датчика, канал: ' + str(Ch) + ' ' + str(s.tm_hour) + ':' + str(
                    s.tm_min) + ':' + str(s.tm_sec))
            elif ord(e.data[0]) == 0xff:
                print 'Некорректный калибровочный коэффициент'
                s_log(u'Некорректный калибровочный коэффициент, канал: ' + str(Ch) + ' ' + str(
                    s.tm_hour) + ':' + str(s.tm_min) + ':' + str(s.tm_sec))
            elif ord(e.data[0]) == 0xfb:
                print 'Измеренное значение слишком мало'
                s_log(u'Измеренное значение слишком мало, канал: ' + str(Ch) + ' ' + str(
                    s.tm_hour) + ':' + str(s.tm_min) + ':' + str(s.tm_sec))
            elif ord(e.data[0]) == 0xfa:
                print 'Измеренное значение слишком велико'
                s_log(u'Измеренное значение слишком велико, канал: ' + str(Ch) + ' ' + str(
                    s.tm_hour) + ':' + str(s.tm_min) + ':' + str(s.tm_sec))
            elif ord(e.data[0]) == 0xf7:
                print 'Датчик отключен'
                s_log(u'Датчик отключен, канал: ' + str(Ch) + ' ' + str(
                    s.tm_hour) + ':' + str(s.tm_min) + ':' + str(s.tm_sec))
            elif ord(e.data[0]) == 0xf6:
                print 'Данные температуры не готовы'
                s_log(u'Данные температуры не готовы ' + str(Ch) + ' ' + str(
                    s.tm_hour) + ':' + str(s.tm_min) + ':' + str(s.tm_sec))
            elif ord(e.data[0]) == 0xf0:
                print 'Значение заведомо неверно'
                s_log(u'Значение заведомо неверно, канал: ' + str(Ch) + ' ' + str(
                    s.tm_hour) + ':' + str(s.tm_min) + ':' + str(s.tm_sec))
        else:
            print 'wtf it needs?'
            s_log(u'Неизвестная ошибка ввода, канал: ' + str(Ch) + ' ' + str(
                s.tm_hour) + ':' + str(s.tm_min) + ':' + str(s.tm_sec))
            if COM.isOpen():
                COM.close()
                COM.open()

# -------------app window--------------------------
# -------------------------------------------------
class MainWindow(QtGui.QMainWindow, Ui_MainWindow):
    temp_signal = QtCore.pyqtSignal(np.ndarray)
    time_signal = QtCore.pyqtSignal(list)
    user_data_signal = QtCore.pyqtSignal(int, int)
    lock_signal = QtCore.pyqtSignal()

    Fan1_On = 0  # fan on/off = 0/1
    Line_65 = 0  # line on=1 line off=0
    Tarray = np.array([[0.0, 0],
                       [0.0, 0],
                       [0.0, 0]])
    T1 = t1 = 0
    Tmax = 220 # предел ТЭНов
    TRate1 = []  # log набора температуры
    deltaTRate1 = 0  # хранение текущей скорости роста температуры
    iconOn = QtGui.QIcon()
    iconOff = QtGui.QIcon()
    iconLock = QtGui.QIcon()
    iconUnlock = QtGui.QIcon()
    MTemp1 = 0.0  # храним вычисленное значение температуры
    WaitText = 'ГОТОВ К ЗАПУСКУ'
    WorkText = 'НАГРЕВ '
    DelayText = 'ВЫДЕРЖКА '
    coldStart1 = 0  # коррекция скорости при отключении датчиков
    coldStart = 0  # запуск программы после загрузки
    Heater1 = 0  # температура тэнов
    pwmDelayCounter0 = 0 # 0 можно менять скважность шим

    lockedBut = True
    State1 = 0  # флаги состояния нагрев/выдержка
    justStarted1 = 0  # флаги начала отсчета времени
    startTime1 = 0
    countdown1 = 0
    level = [0 /100, 25 / 100, 50 / 100, 75 / 100, 100 / 100]

    #FI = 300
    #FT = 15

    Fan1Interval = FI  # запуск по 15 через 300 сек
    Fan1Time = FT

    file_name_1 = ''

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        # --------------ini set--------------------
        self.setWindowFlags(Qt.FramelessWindowHint)

        read_settings()
        self.call_ini_set()  # set css from metrocss+T-temp and t-delay from settings

        call_board_ini()  # set raspberry ports
        self.set_adc()  # start ADC data
        self.set_hotkeys()

        self.SetVirtualButtons()

        # --------------prog buttons set--------------------
        self.p1_1.pressed.connect(self.SelectProg)
        self.p1_2.pressed.connect(self.SelectProg)
        self.p1_3.pressed.connect(self.SelectProg)
        self.p1_4.pressed.connect(self.SelectUserProg)

        self.user_data_signal.connect(self.set_user_data, QtCore.Qt.QueuedConnection)

        # --------------params buttons set--------------------
        self.Over_Heat_Ctrl_1.pressed.connect(self.ParamsSet)
        self.Sensor1_1.pressed.connect(self.ParamsSet)
        self.Sensor1_2.pressed.connect(self.ParamsSet)
        self.Fan1_Allow.pressed.connect(self.ParamsSet)

        # --------------startstop buttons set--------------------

        self.StartVirt1.pressed.connect(self.StartStop)
        self.StopVirt1.pressed.connect(self.StartStop)

        # --------------fans buttons set--------------------
        self.Fan1.pressed.connect(self.SetFans)
        # --------------history button set--------------------
        self.HistoryGraph.pressed.connect(self.ViewHistory)

        # --------------history button set--------------------
        self.lockVirt.pressed.connect(self.UnlockButtons)
        self.lock_signal.connect(self.LockButtons, QtCore.Qt.QueuedConnection)

    # -------------------------------------------------
    # ---------------end app window--------------------


    # ----------------------------methods------------------------------
    def pwmSet(self, port, value, Stop = False):
        '''
        управляем включением внешних устройств (ШИМ или просто вкл/выкл)
        :param port: имя порта, к примеру Fan1
        :param value: 0.0-1.0
        :param Stop = True обойти ограничение по частоте вызовов смены скважности
        :return:
        '''
        global portIsBusy
        # отсекаем вызовы по смене скважности
        if port == SSRPwm0:
            if self.pwmDelayCounter0 >0 and (not Stop):
                self.pwmDelayCounter0 += 1
                if self.pwmDelayCounter0 > round(Freq, 0): self.pwmDelayCounter0 = 0
                print 'return'
                return
            else: self.pwmDelayCounter0 = (self.pwmDelayCounter0 + 1) * int(not Stop)

        while portIsBusy:
            print 'pwm busy', portIsBusy
            time.sleep(0.05)
        portIsBusy = True
        try:
            print 'r.OE '+ portTuple[port], MU.writeFloat24('r.OE', port, value)
            self.tempthread.counter2 += 1
        except Owen.OwenProtocolError:
            try:
                print 'r.OE ' + portTuple[port], MU.writeFloat24('r.OE', port, value)
                self.tempthread.counter2 += 1
            except Owen.OwenProtocolError as err:
                print err
                print 'Ошибка установки состояния порта ', portTuple[port]
                s_log(u'Ошибка установки состояния порта '+ portTuple[port])
                self.tempthread.counter += 1
        portIsBusy = False


    def time_msg(self, out):
        '''
        :param out: список строковых параметров времени
        :return: ничего
        '''

        self.labeloftime.setText(
            _translate(
                "Calibrator",
                "<html><head/><body><p align=\"center\"><span style=\" font-size:16pt; font-weight:400;\">%s</span></p>"
                "<p align=\"center\"><span style=\" font-size:26pt; font-weight:400;\">%s</span></p>"
                "<p align=\"center\"><span style=\" font-size:16pt; font-weight:400;\">%s</span></p>"
                "</body></html>" % (out[0], out[1], out[2]), None))
        if self.coldStart == 1:
            self.ShowResults(self.Tarray)
        self.ErrorPanel.setHtml(metrocss.Show_err(error_buffer))

    @pyqtSlot()
    def LockButtons(self):
        self.lockedBut = True
        self.lockbut.setIcon(self.iconLock)
        self.lockbut.setStyleSheet(metrocss.SetButtons_passive)

    @pyqtSlot()
    def UnlockButtons(self):
        sender = self.sender()
        longpressed = sender.longpressed
        if longpressed == 0: return
        self.lockedBut = False
        self.lockbut.setIcon(self.iconUnlock)
        self.lockbut.setStyleSheet(metrocss.SetButtons_active)
        self.lockthread.start()

    @pyqtSlot()
    def ViewHistory(self):
        if self.lockedBut: return
        self.HistoryGraph.setStyleSheet(metrocss.prog_active)
        self.LogsView = GraphWindow(self)
        self.LogsView.show()
        self.HistoryGraph.setStyleSheet(metrocss.prog_passive)

    @pyqtSlot()
    def DoMainWork(self):
        global file_name_1
        i = 0
        lim = 1.0

        self.CleanAir()
        # it=0

        if sets['OH_ctrl_1'] == 1 and self.Heater1 > self.Tmax:
            lim = 0.0
        else: lim = 1.0


        if self.justStarted1 == 0 and self.Line_65:
            self.startTime1 = datetime.datetime.now()
            self.justStarted1 = 1
            self.State1 = 0
            self.pwmSet(Cont1, 1)
            file_name_1 = str(int(time.time())) + '_1_' + str(self.T1) + '.txt'

        if self.Line_65 == 1:
            # ---------heaters control------------------------
            if self.State1 == 0:
                delta1 = str(datetime.datetime.now() - self.startTime1)[:7]
                # ----проверяем границы температура относительно уставки
                if self.MTemp1 < (self.T1 - 15):
                    self.pwmSet(SSRPwm0, self.level[4] * lim)
                    i = self.level[4] * 100  * lim
                    self.InfoPanel1.setHtml(metrocss.SetInfoPanelText(self.WorkText + delta1 + " " + str(i) + "%"))

                elif (self.T1 - 15) <= self.MTemp1 < self.T1:
                    if self.deltaTRate1 >= 5:
                        self.pwmSet(SSRPwm0, self.level[0] * lim)
                        i = self.level[0]  * 100 * lim
                    elif 3 <= self.deltaTRate1 < 5:
                        self.pwmSet(SSRPwm0, self.level[1] * lim)
                        i = self.level[1] * 100 * lim
                    elif 1 <= self.deltaTRate1 < 3:
                        self.pwmSet(SSRPwm0, self.level[2] * lim)
                        i = self.level[2] * 100 * lim
                    elif self.deltaTRate1 < 1:
                        self.pwmSet(SSRPwm0, self.level[4] * lim)
                        i = self.level[4] * 100 * lim

                    self.InfoPanel1.setHtml(metrocss.SetInfoPanelText(self.WorkText + delta1 + " " + str(i) + "%"))
                # ----уходим на выдержку-------------------------
                elif self.MTemp1 >= self.T1:
                    self.pwmSet(SSRPwm0, self.level[0] * lim)
                    self.State1 = 1
                    self.startTime1 = datetime.datetime.now()
                    self.countdown1 = datetime.timedelta(minutes=self.t1)
                    delta1 = datetime.datetime.now() - self.startTime1
                    delta1 = str((self.countdown1 - delta1))[:7]
                    self.InfoPanel1.setHtml(metrocss.SetInfoPanelText(self.DelayText + str(self.countdown1)[:7]))

            elif self.State1 == 1:
                delta1 = datetime.datetime.now() - self.startTime1

                # --------обратный отсчет выдержки------------------------
                if delta1.total_seconds() / 60 <= self.t1:
                    delta1 = str((self.countdown1 - delta1))[:7]

                    if self.MTemp1 >= self.T1:
                        self.pwmSet(SSRPwm0, self.level[0] * lim)
                        i = self.level[0] * 100 * lim
                    elif (self.T1 - 1) <= self.MTemp1 < self.T1:
                        self.pwmSet(SSRPwm0, self.level[1] * lim)
                        i = self.level[1] * 100 * lim
                    elif (self.T1 - 2) <= self.MTemp1 < (self.T1 - 1):
                        self.pwmSet(SSRPwm0, self.level[2] * lim)
                        i = self.level[2] * 100 * lim
                    elif (self.T1 - 4) <= self.MTemp1 < (self.T1 - 2):
                        self.pwmSet(SSRPwm0, self.level[3] * lim)
                        i = self.level[3] * 100 * lim
                    elif (self.T1 - 4) > self.MTemp1:
                        self.pwmSet(SSRPwm0, self.level[4] * lim)
                        i = self.level[4] * 100 * lim
                    self.InfoPanel1.setHtml(metrocss.SetInfoPanelText(self.DelayText + delta1 + " " + str(i) + "%"))

                # --------работа сделана------------------------
                elif delta1.total_seconds() / 60 > self.t1:
                    self.StartButton1.setStyleSheet(metrocss.StartButton_active)
                    self.StopButton1.setStyleSheet(metrocss.StopButton_passive)
                    self.setWorkzonePassive('1')
                    self.Line_65 = 0
                    self.InfoPanel1.setHtml(metrocss.SetInfoPanelText(self.WaitText))
                    self.pwmSet(SSRPwm0, self.level[0], Stop=True)
                    self.State1 = 0
                    self.justStarted1 = 0
                    self.pwmSet(Cont1, 0)
            save_log(file_name_1, self.MTemp1, i, self.State1, self.Fan1_On, self.Heater1)


    @pyqtSlot()
    def CleanAir(self):  # работа вентиляторов в цикле полимеризации
        if sets['Fan1_Allow'] and self.Line_65 and (round(self.MTemp1) in range(150, 200)):
            if self.Fan1Interval > 0:
                self.Fan1Interval -= 1
            elif self.Fan1Interval == 0:
                if self.Fan1Time > 0:
                    self.Fan1Time -= 1
                    if self.Fan1_On:
                        pass
                    else:
                        self.SetFans(1)
                elif self.Fan1Time == 0:
                    self.Fan1Interval = FI
                    self.Fan1Time = FT
                    if self.Fan1_On:
                        self.SetFans(1)
                    else:
                        pass

    def SetFans(self, Line=0):  # триггер вентиляторов
        if Line == 1:
            if self.Fan1_On == 0:
                self.Fan1_On = 1
                self.pwmSet(Fan1, self.Fan1_On)
                self.Fan1.setIcon(self.iconOn)
            else:
                self.Fan1_On = 0
                self.pwmSet(Fan1, self.Fan1_On)
                self.Fan1.setIcon(self.iconOff)

        else:
            sender = self.sender()
            if sender == self.Fan1:
                if self.Fan1_On == 0:
                    sender.setIcon(self.iconOn)
                    self.Fan1_On = 1
                    self.pwmSet(Fan1, self.Fan1_On)
                else:
                    sender.setIcon(self.iconOff)
                    self.Fan1_On = 0
                    self.pwmSet(Fan1, self.Fan1_On)

    def setWorkzonePassive(self, point):  # ожидающая рабочая зона
        if point == '1':
            self.Channel1.setStyleSheet(metrocss.Channel_waiting)
            self.Channel2.setStyleSheet(metrocss.Channel_waiting)
            self.Channel3.setStyleSheet(metrocss.Channel_waiting)

        getattr(self, 'Counter' + str(point)).setStyleSheet(metrocss.Rate_Counter_waiting)
        getattr(self, 'Rate' + str(point)).setStyleSheet(metrocss.Rate_Counter_waiting)
        getattr(self, 'MainTemp' + str(point)).setStyleSheet(metrocss.MainTemp_waiting)
        getattr(self, 'InfoPanel' + str(point)).setStyleSheet(metrocss.InfoPanel_waiting)
        getattr(self, 'SetTemp' + str(point)).setStyleSheet(metrocss.Sets_waiting)
        getattr(self, 'SetDelay' + str(point)).setStyleSheet(metrocss.Sets_waiting)

    def setWorkzoneActive(self, point):  # оранжевая рабочая зона
        if point == '1':
            self.Channel1.setStyleSheet(metrocss.Channel_working)
            self.Channel2.setStyleSheet(metrocss.Channel_working)
            self.Channel3.setStyleSheet(metrocss.Channel_working)

        getattr(self, 'Counter' + str(point)).setStyleSheet(metrocss.Rate_Counter_working)
        getattr(self, 'Rate' + str(point)).setStyleSheet(metrocss.Rate_Counter_working)
        getattr(self, 'MainTemp' + str(point)).setStyleSheet(metrocss.MainTemp_working)
        getattr(self, 'InfoPanel' + str(point)).setStyleSheet(metrocss.InfoPanel_working)
        getattr(self, 'SetTemp' + str(point)).setStyleSheet(metrocss.Sets_working)
        getattr(self, 'SetDelay' + str(point)).setStyleSheet(metrocss.Sets_working)

    @pyqtSlot()
    def StartStop(self):  # кнопки старт стоп
        sender = self.sender()
        name = sender.name
        s = len(name)
        point = name[s - 1]
        longpressed = sender.longpressed
        if longpressed == 0: return

        if name[:5] == 'Start':
            if point == '1' and self.Line_65 == 0:
                self.StartButton1.setStyleSheet(metrocss.StartButton_passive)
                self.StopButton1.setStyleSheet(metrocss.StopButton_active)
                self.setWorkzoneActive(point)
                self.Line_65 = 1
                sets['Counter1'] += 1
                self.Counter1.setHtml(metrocss.Show_Counter(sets['Counter1']))
                save_settings(sets)

        elif name[:4] == 'Stop':
            if point == '1' and self.Line_65 == 1:
                self.StartButton1.setStyleSheet(metrocss.StartButton_active)
                self.StopButton1.setStyleSheet(metrocss.StopButton_passive)
                self.setWorkzonePassive(point)
                self.Line_65 = 0
                self.InfoPanel1.setHtml(metrocss.SetInfoPanelText(self.WaitText))
                self.pwmSet(SSRPwm0, 0, Stop=True)
                self.startHeat1 = 0
                self.startDelay1 = 0
                self.justStarted1 = 0
                self.pwmSet(Cont1, 0)

                self.Fan1Interval = FI
                self.Fan1Time = FT
                if self.Fan1_On: self.SetFans(1)

    def All_is_Clear(self):  # корректное завершение
        self.tempthreadcontrol(0)
        self.timelabel.stop()
        self.close()

    def __del__(self):  # какая-то системная
        self.ui = None

    @pyqtSlot()
    def ParamsSet(self):  # работа кнопок Параметры
        if self.lockedBut: return
        sender = self.sender()

        # ------------------heater sensors----------------------
        if sender == self.Over_Heat_Ctrl_1:
            if sets['OH_ctrl_1'] == 1:
                self.Over_Heat_Ctrl_1.setStyleSheet(metrocss.SetButtons_passive)
                sets['OH_ctrl_1'] = 0
            else:
                self.Over_Heat_Ctrl_1.setStyleSheet(metrocss.SetButtons_active)
                sets['OH_ctrl_1'] = 1

        # ---------------main sensors------------------
        if sender == self.Sensor1_1:
            self.coldStart1 = 0
            if sets['sensor1_1'] == 1:
                self.Sensor1_1.setStyleSheet(metrocss.SetButtons_passive)
                sets['sensor1_1'] = 0
                if sets['sensor1_2'] == 0:
                    self.Sensor1_2.setStyleSheet(metrocss.SetButtons_active)
                    sets['sensor1_2'] = 1
            else:
                self.Sensor1_1.setStyleSheet(metrocss.SetButtons_active)
                sets['sensor1_1'] = 1

        if sender == self.Sensor1_2:
            self.coldStart1 = 0
            if sets['sensor1_2'] == 1:
                self.Sensor1_2.setStyleSheet(metrocss.SetButtons_passive)
                sets['sensor1_2'] = 0
                if sets['sensor1_1'] == 0:
                    self.Sensor1_1.setStyleSheet(metrocss.SetButtons_active)
                    sets['sensor1_1'] = 1
            else:
                self.Sensor1_2.setStyleSheet(metrocss.SetButtons_active)
                sets['sensor1_2'] = 1

        # --------------------Fan Prams------------------------
        if sender == self.Fan1_Allow:
            if sets['Fan1_Allow'] == 1:
                self.Fan1_Allow.setStyleSheet(metrocss.SetButtons_passive)
                sets['Fan1_Allow'] = 0
                if self.Line_65:
                    self.Fan1Interval = FI
                    self.Fan1Time = FT
                    if self.Fan1_On: self.SetFans(1)
            else:
                self.Fan1_Allow.setStyleSheet(metrocss.SetButtons_active)
                sets['Fan1_Allow'] = 1

        save_settings(sets)

    def set_user_data(self, T, t):  # ловля сигнала модального окна ввода настроек температуры и выдержки
        if self.point == 1:
            self.SetTemp1.setHtml(metrocss.settemp(T))
            self.SetDelay1.setHtml(metrocss.setdelay(t))
            self.T1 = T
            self.t1 = t

    @pyqtSlot()
    def SelectUserProg(self):  # отработка нажатия кнопки пользовательская программа
        sender = self.sender()
        name = sender.objectName()
        point = name[1]
        self.point = int(point)
        if self.point == 1 and self.Line_65 == 0:
            self.clear_buttons(self.point)
            sender.setStyleSheet(metrocss.prog_active)
            self.AskWindow = UserData(self.user_data_signal, self)
            self.AskWindow.show()
            self.AskWindow.move(313, 195)

    @pyqtSlot()
    def SelectProg(self):  # кнопки выбора программ
        sender = self.sender()
        name = sender.objectName()
        if name[1] == '1':
            if self.Line_65 == 0:
                prog = int(name[3])
                line = 1
                self.set_prog(prog, line)
            else:
                pass

    @pyqtSlot()
    def set_hotkeys(self):  # горячие клавиши для завершения и сворачивания
        # свернуть окно по CTRL+Hself.SetTemp2.setStyleSheet
        self.minact = QAction(self)
        self.minact.setShortcut("CTRL+H")
        self.minact.setShortcutContext(Qt.ApplicationShortcut)
        self.addAction(self.minact)
        QObject.connect(self.minact, SIGNAL("triggered()"), lambda: self.setWindowState(Qt.WindowMinimized))
        # Exit CTRL+Q
        self.actq = QAction(self)
        self.actq.setShortcut("CTRL+Q")
        self.actq.setShortcutContext(Qt.ApplicationShortcut)
        self.addAction(self.actq)
        QObject.connect(self.actq, SIGNAL("triggered()"), self.All_is_Clear)
        # Exit CTRL+Й
        self.actqr = QAction(self)
        self.actqr.setShortcut("CTRL+Й")
        self.actqr.setShortcutContext(Qt.ApplicationShortcut)
        self.addAction(self.actqr)
        QObject.connect(self.actqr, SIGNAL("triggered()"), self.All_is_Clear)

    @pyqtSlot()
    def set_adc(self):  # запуск ацп в потоке
        self.tempthread = TempThread(self.temp_signal)
        self.temp_signal.connect(self.got_worker_msg, QtCore.Qt.QueuedConnection)
        self.tempthreadcontrol(1)

    def closeEvent(self, event):  # переопределяем закрытие окна
        self.All_is_Clear()

    def ShowResults(self, Tin):  # вывод температуры на рабочую зону
        alph = self.coldStart1 & 1
        alph = 2 - int(not alph)

        # -------------рассчитываем температуры по разрешенным датчикам---------
        if sets['sensor1_1'] == 1 and sets['sensor1_2'] == 1:
            self.MTemp1 = (self.MTemp1 * self.coldStart1 + (Tin[1][0] + Tin[2][0]) / 2) / alph
            self.MainTemp1.setHtml(metrocss.Show_Main_Temp("%.1f" % self.MTemp1))
            self.Channel1.setHtml(metrocss.Show_temp(Tin[1][0]))
            self.Channel2.setHtml(metrocss.Show_temp(Tin[2][0]))
        elif sets['sensor1_1'] == 0 and sets['sensor1_2'] == 1:
            self.MTemp1 = (self.MTemp1 * self.coldStart1 + Tin[2][0]) / alph
            self.MainTemp1.setHtml(metrocss.Show_Main_Temp("%.1f" % self.MTemp1))
            self.Channel1.setHtml(metrocss.Show_temp("NaN"))
            self.Channel2.setHtml(metrocss.Show_temp(Tin[2][0]))
        elif sets['sensor1_1'] == 1 and sets['sensor1_2'] == 0:
            self.MTemp1 = (self.MTemp1 * self.coldStart1 + Tin[1][0]) / alph
            self.MainTemp1.setHtml(metrocss.Show_Main_Temp("%.1f" % self.MTemp1))
            self.Channel1.setHtml(metrocss.Show_temp(Tin[1][0]))
            self.Channel2.setHtml(metrocss.Show_temp("NaN"))

        self.Heater1 = Tin[3][0]

        self.Channel3.setHtml(metrocss.Show_temp(self.Heater1))  # Тэны всегда!

        # -------------работаем со стеком значений температур---------
        if self.coldStart == 0:
            for i in range(60):
                self.TRate1.append(self.MTemp1)

            self.coldStart = 1
        else:
            self.TRate1.append(self.MTemp1)

        if self.coldStart1 == 0:
            self.TRate1 = []
            for i in range(60):
                self.TRate1.append(self.MTemp1)
            self.coldStart1 = 1


        # -------------вычисляем скорость изменения температуры по стеку---------
        self.deltaTRate1 = (self.deltaTRate1 + self.MTemp1 - self.TRate1.pop(0)) / 2

        self.Rate1.setHtml(metrocss.Show_Rate(self.deltaTRate1))

        # -----вызываем обработку состояния вкл/выкл линии по полученным данным----
        self.DoMainWork()


    def got_worker_msg(self, Va):  # ловля сигнала от АЦП
        self.Tarray = Va
        if self.coldStart == 0:
            self.ShowResults(self.Tarray)

    def tempthreadcontrol(self, command):  # запуск/остановка потока
        if command == 1:
            self.tempthread.isRun = True
            self.tempthread.start()
        elif command == 0:
            self.tempthread.stop()

    def clear_buttons(self, line):  # установка кнопок в серое состояние при смене программы
        if line == 1:
            self.p1_1.setStyleSheet(metrocss.prog_passive)
            self.p1_2.setStyleSheet(metrocss.prog_passive)
            self.p1_3.setStyleSheet(metrocss.prog_passive)
            self.p1_4.setStyleSheet(metrocss.prog_passive)

    def set_prog(self, prog, line):  # подпрограммы кнопок переключения программы
        if line == 1:
            self.clear_buttons(1)
            if prog == 1:
                self.p1_1.setStyleSheet(metrocss.prog_active)
                self.SetTemp1.setHtml(metrocss.settemp(180))
                self.SetDelay1.setHtml(metrocss.setdelay(15))
                self.T1 = 180
                self.t1 = 15
                sets['start_prog1'] = 1
            if prog == 2:
                self.p1_2.setStyleSheet(metrocss.prog_active)
                self.SetTemp1.setHtml(metrocss.settemp(190))
                self.SetDelay1.setHtml(metrocss.setdelay(10))
                self.T1 = 190
                self.t1 = 10
                sets['start_prog1'] = 2
            if prog == 3:
                self.p1_3.setStyleSheet(metrocss.prog_active)
                self.SetTemp1.setHtml(metrocss.settemp(200))
                self.SetDelay1.setHtml(metrocss.setdelay(10))
                self.T1 = 200
                self.t1 = 10
                sets['start_prog1'] = 3

        save_settings(sets)

    @pyqtSlot()
    def call_ini_set(self):  # установка первоначального & состояния из файла настроек
        self.iconOff.addPixmap(QtGui.QPixmap("Fanoff.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.iconOn.addPixmap(QtGui.QPixmap("Fanon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.iconLock.addPixmap(QtGui.QPixmap("lock.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.iconUnlock.addPixmap(QtGui.QPixmap("unlock.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)

        # ---------lock buttons-----------
        self.lockedBut = True
        self.lockbut.setIcon(self.iconLock)
        self.lockbut.setStyleSheet(metrocss.SetButtons_passive)
        self.lockthread = LockThread(self.lock_signal)

        # ---------------timelabel--------------------------
        self.timelabel = TimeThread(self.time_signal)
        self.time_signal.connect(self.time_msg, QtCore.Qt.QueuedConnection)
        self.timelabel.isRun = True
        self.timelabel.start()
        # ---------initial default prog set-----------
        if sets['start_prog1'] == 1:
            self.set_prog(1, 1)
        if sets['start_prog1'] == 2:
            self.set_prog(2, 1)
        if sets['start_prog1'] == 3:
            self.set_prog(3, 1)

        # ---------heaters set--------------------
        if sets['OH_ctrl_1'] == 1:
            self.Over_Heat_Ctrl_1.setStyleSheet(metrocss.SetButtons_active)

        if sets['sensor1_1'] == 1:
            self.Sensor1_1.setStyleSheet(metrocss.SetButtons_active)

        if sets['sensor1_2'] == 1:
            self.Sensor1_2.setStyleSheet(metrocss.SetButtons_active)

        # ---------fans set--------------------
        if sets['Fan1_Allow'] == 1:
            self.Fan1_Allow.setStyleSheet(metrocss.SetButtons_active)

        # ---------counter set--------------------
        self.Counter1.setHtml(metrocss.Show_Counter(sets['Counter1']))

        # ---------Infopanel set--------------------
        self.InfoPanel1.setHtml(metrocss.SetInfoPanelText(self.WaitText))

    def SetVirtualButtons(self):  # рисуем кнопки с длинным нажатием

        self.StartVirt1 = LongButton(self.centralwidget, name="StartVirt1")
        self.StartVirt1.setGeometry(QtCore.QRect(325, 202, 134, 139))
        self.setButProps(self.StartVirt1)

        self.StopVirt1 = LongButton(self.centralwidget, name="StopVirt1")
        self.StopVirt1.setGeometry(QtCore.QRect(325, 354, 134, 139))
        self.setButProps(self.StopVirt1)


        self.lockVirt = LongButton(self.centralwidget, name="lockVirt")
        self.lockVirt.setGeometry(QtCore.QRect(717, 790, 150, 148))
        self.setButProps(self.lockVirt)

    def setButProps(self, obj):
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(obj.sizePolicy().hasHeightForWidth())
        obj.setSizePolicy(sizePolicy)
        obj.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        obj.setFocusPolicy(QtCore.Qt.NoFocus)
        obj.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        obj.setAcceptDrops(False)
        obj.setStyleSheet(_fromUtf8("border-style: outset;background-color: none;"))


# ------------globals func-----------------------------

def save_log(file_name, temp, power, state, fan_state, heater):
    t = time.time()
    if file_name != '':
        with open("logs/" + file_name, "a") as log_file:
            log_file.write(str(t) + ',' + str(round(temp, 1)) + ',' + str(power) + ',' + str(state) + ',' + str(
                fan_state) + ',' + str(heater) + '\n')


def read_settings():
    global sets
    try:
        with open('settings.txt', 'rt') as csvfile:
            spamreader = csv.reader(csvfile, delimiter='=', quotechar='|')
            for row in spamreader:
                k, v = row
                try:
                    sets[k] = int(v)
                except ValueError:
                    pass

    except IOError:
        sets = metrocss.a
        save_settings(sets)


def save_settings(sets):
    with open('settings.txt', 'wt') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter='=',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for key, val in sets.items():
            spamwriter.writerow([key, val])


def call_board_ini():

    it = True
    counter = 0
    while it:
        try:
            devName = MVA.GetDeviceName()
            _name = u'Модуль ввода: {}'.format(devName)
            #s_log(_name)
            print 'Модуль ввода: ' + devName
            #Прошивка
            result = MVA.GetFirmwareVersion()
            _firm = u'Версия ПО: {}'.format(result)
            s_log(_name + ' ' + _firm)
            print 'Версия ПО: ' + result
            it = False
        except Owen.OwenProtocolError:
            counter += 1
            print(u'Модуль ввода недоступен ' + str(counter) + ' ' + u'раз')
            s_log(u'Модуль ввода недоступен ' + str(counter) + ' ' + u'раз')
            if counter > 9: it = False
            if COM.isOpen():
                COM.close()
                COM.open()

    it = True
    counter = 0
    while it:
        try:
            devName = MU.GetDeviceName()
            _name = u'Модуль вывода: {}'.format(devName)
            print 'Модуль вывода: ' + devName
            #Прошивка
            result = MU.GetFirmwareVersion()
            _firm = u'Версия ПО: {}'.format(result)
            print 'Версия ПО: ' + result
            s_log(_name + ' ' + _firm)
            it = False
        except Owen.OwenProtocolError:
            counter += 1
            print('Модуль вывода недоступен ' + str(counter) + ' раз')
            s_log(u'Модуль вывода недоступен ' + str(counter) + ' ' + u'раз')
            if counter > 9: it = False
            if COM.isOpen():
                COM.close()
                COM.open()

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

