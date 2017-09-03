# -*- coding: utf-8 -*-
from operator import methodcaller
import os, time
from PyQt4 import QtCore, QtGui, uic
from PyQt4.Qt import Qt
import numpy as np
import pyqtgraph as pg

MainInterfaceWindow = "graphwindow.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(MainInterfaceWindow)

DEGREE = u"\u00B0" + 'C'


class GraphWindow(QtGui.QMainWindow, Ui_MainWindow):
    """MainWindow inherits QMainWindow"""
    path = "logs/"
    lf1 = []

    def __init__(self, parent=None):
        super(GraphWindow, self).__init__(parent)
        Ui_MainWindow.__init__(self)
        pg.setConfigOption('background', (194, 194, 194))
        pg.setConfigOption('foreground', (0, 0, 0))
        self.setupUi(self)
        self.setWindowModality(QtCore.Qt.WindowModal)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.listWidget.verticalScrollBar().setStyleSheet(_fromUtf8(
            "QScrollBar:vertical {width: 40px; background: rgb(194, 194, 194); margin: 0px;}\n"
            "QScrollBar::handle:vertical {min-height: 40px;}\n"
            "QScrollBar::sub-line:vertical {subcontrol-position: top; subcontrol-origin: margin; height: 70px; }\n"
            "QScrollBar::add-line:vertical {subcontrol-position: bottom; subcontrol-origin: margin; height: 70px; }\n"
            "QScrollBar::down-arrow:vertical, QScrollBar::up-arrow:vertical {background: NONE;}\n"
            "QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {background: NONE;}"))

        self.ExitButton.pressed.connect(self.exit)
        self.listWidget.itemClicked.connect(self.letsgo)

        self.sceneW = int(self.graphicsView.width())
        self.sceneH = int(self.graphicsView.height())
        self.graphicsView.addLegend(size=None, offset=(self.sceneW * 0.77, self.sceneH * 0.22))
        self.searchLogs()

    def __del__(self):
        self.ui = None

    def exit(self):  # Funkzija zavershenija raboti okna.
        self.close()

    def searchLogs(self):  # Funkzija vivoda imen failov v spisok

        ld = os.listdir(self.path)  # Berem spisok failov  directorija

        lf = []  # Fil'truem faili s rasshireniem .txt - log faili
        for i in range(len(ld)):
            if ld[i].endswith(".txt"):
                lf.append(ld[i])

        lf.sort()  # сортировка по времени
        lf.reverse()  # в обратном порядке

        self.lf1 = []
        for i in range(len(lf)):
            self.lf1.append([])
            self.lf1[i].append(lf[i])
            t = lf[i].split('_')[0]
            s = time.localtime(float(t))
            l = lf[i].split('_')[1]
            if l == "1":
                l = u"6,5 м"
            else:
                l = u"3,5 м"

            if s.tm_min < 10:
                minutes = '0' + str(s.tm_min)
            else:
                minutes = str(s.tm_min)
            s = '%s-%s-%s %s:%s' % (
            str(s.tm_year)[2:], str(s.tm_mon), str(s.tm_mday), str(s.tm_hour), minutes) + u" Линия: " + l
            self.lf1[i].append(s)

        for i in range(len(lf)):  # Pomeschaem imena log failov v vizual'nij spisok
            self.listWidget.addItem(self.lf1[i][1])

        try:
            self.listWidget.setCurrentRow(0)
            self.letsgo()
        except IndexError:
            pass


    def letsgo(self):  # выбор файла в списке
        self.statusBar.showMessage(
            u"Имя лога: " + self.lf1[self.listWidget.currentRow()][0])  # Vivodim coobschenie v statusBar.
        self.draw()  # Vizivaem funkziju prorisovki grafika

    def draw(self):  # рисуем график

        file_name = self.lf1[self.listWidget.currentRow()][0]  # параметр функции - имя лог файла

        ust = file_name.split('_')[-1]  # Выделение уставки из имени файла
        ust = int(ust.split('.')[0])

        try:  # читаем лог файл
            with open(self.path + file_name) as f:
                lines = f.read().splitlines()  # Читаем файл по строкам
        except IOError:
            self.graphicsView.clear()
            self.delLegend()
            self.graphicsView.setTitle(title=u'Ошибка чтения файла')
            return

        try:
            if lines[-1] == '': #работаем с битыми логами
                lines.pop()
            if len(lines[-1]) not in range(27, 34):
                lines.pop()
        except IndexError:
            self.graphicsView.clear()
            self.delLegend()
            self.graphicsView.setTitle(title=u'Пустой файл')
            return

        # Временный массив для разбиения строк на составлящие

        cpw = list(map(methodcaller("split", ","), lines))

        timeAxis = []  # Заполнение массива координат графиков
        tempLine = []
        powerLine = []
        stateLine = []
        fanLine = []
        heatLine = []
        try:
            for i in range(len(cpw)):
                timeAxis.append(float(cpw[i][0]))
                tempLine.append(float(cpw[i][1]))
                powerLine.append(float(cpw[i][2]))
                stateLine.append(float(cpw[i][3]))
                fanLine.append(float(cpw[i][4]))
                heatLine.append(float(cpw[i][5]))
        except ValueError:
            self.graphicsView.clear()
            self.delLegend()
            self.graphicsView.setTitle(title=u'Ошибка координат')
            return
        length = len(timeAxis)
        delt = 0
        x0 = timeAxis[0]
        x1 = timeAxis[-1]
        itera = 0
        try:
            while delt == 0:
                if stateLine[itera] == 1:
                    delt = timeAxis[itera]
                    index = itera
                if itera < length:
                    itera += 1
        except IndexError:
            delt = timeAxis[-1]
            index = -1
        cpw = []  # clear memory
        lines = []

        dx = x1 - delt

        for i in range(length):  # Вычитание нулевой точки по оси x
            timeAxis[i] = timeAxis[i] - x0

        timeAxis = np.array(timeAxis)
        tempLine = np.array(tempLine)
        powerLine = np.array(powerLine)
        stateLine = np.array(stateLine)
        fanLine = np.array(fanLine)
        heatLine = np.array(heatLine)
        ustLine = np.arange(length)
        ustLine[::] = ust

        maxTemp = tempLine.max()  # поиск максимумов координат графиков
        maxPower = powerLine.max()
        maxHeat = heatLine.max()

        minTemp = tempLine.min()
        minHeat = heatLine.min()

        minimum = minTemp
        maximum = ust

        if minTemp > minHeat:
            minimum = minHeat

        if maximum < maxHeat:
            maximum = maxHeat
        elif maximum < maxTemp:
            maximum = maxTemp

        timeAxis /=  60

        self.graphicsView.setLimits(xMin=0, xMax=timeAxis[-1], yMin=minimum, yMax=maximum)

        if maxPower != 0: #нормировка на примерно половину высоты графика температуры
            powerLine = (maximum - minimum) * powerLine / (maxPower * 2) + minimum

        stateLine = (maximum - minimum) * stateLine / 2.1 + minimum
        fanLine = (maximum - minimum) * fanLine / 2.2 + minimum

        self.graphicsView.clear()
        self.delLegend()

        labelStyle = {'color': '#000', 'font-size': '12pt'}
        self.graphicsView.setLabel('left', u'Температура, ' + DEGREE, **labelStyle)
        self.graphicsView.setLabel('bottom', u'Время, мин', **labelStyle)
        # self.graphicsView.getAxis('bottom').setStyle(tickTextOffset=300)

        self.graphicsView.showGrid(x=True, y=True, alpha=1)

        self.graphicsView.plot(x=timeAxis, y=tempLine, name=self.SetInfoPanelText('Температура'),
                               pen=pg.mkPen('k', width=3))
        self.graphicsView.plot(x=timeAxis, y=powerLine, name=self.SetInfoPanelText('Мощность'),
                               pen=pg.mkPen('r', width=3))
        self.graphicsView.plot(x=timeAxis, y=heatLine, name=self.SetInfoPanelText('ТЭНы'),
                               pen=pg.mkPen('y', width=3))
        self.graphicsView.plot(x=timeAxis, y=stateLine, name=self.SetInfoPanelText('Состояние'),
                               pen=pg.mkPen('m', width=3))
        self.graphicsView.plot(x=timeAxis, y=fanLine, name=self.SetInfoPanelText('Вентиляторы'),
                               pen=pg.mkPen('g', width=3))
        self.graphicsView.plot(x=timeAxis, y=ustLine, name=self.SetInfoPanelText('Уставка ' + str(ust)),
                               pen=pg.mkPen('b', width=4))
        # self.graphicsView.addLine(y=maxHeat, name=self.SetInfoPanelText('ТЭН'), pen=pg.mkPen('y', width=3))
        # self.graphicsView.addLine(x=timeAxis[index], name=self.SetInfoPanelText('Выдержка'), pen=pg.mkPen('m', width=3))

        delay = dx // 60
        delay = int(delay % 60)
        delay = str(delay) + ' мин'  # Выдержка

        s = time.localtime(float(x0))
        m = str(s.tm_min)
        if len(m) == 1:
            m = '0' + m
        h = str(s.tm_hour)
        if len(h) == 1:
            h = '0' + h
        t_start = h + ':' + m  # Начало

        s = time.localtime(float(x1))
        m = str(s.tm_min)
        if len(m) == 1:
            m = '0' + m
        h = str(s.tm_hour)
        if len(h) == 1:
            h = '0' + h
        t_end = h + ':' + m  # # Окончание

        self.graphicsView.setTitle(title=self.SetInfoPanelText(
            'Начало: ' + t_start + ', Окончание: ' + t_end + ', Выдержка: ' + delay + ', ТЭН: ' + str(
                maxHeat)))

    def SetInfoPanelText(self, text):
        out = _translate("GraphWindow",
                         "<body style=\" font-family:\'Free Helvetian\'; font-size:14pt;\"><p>%s</p></body>" % text,
                         None)
        return out

    def delLegend(self):
        try:
            self.graphicsView.plotItem.legend.items = []
        except AttributeError:
            pass

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
