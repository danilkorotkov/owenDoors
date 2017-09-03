# -*- coding: utf8 -*-

from TOwen import Owen
from TSystem import MySerial
import serial.rs485
import time

#Owen.test()#прогоняем тест библиотеки

#создаем последовательный порт
try:
    COM = MySerial.ComPort('/dev/ttyUSB0', 57600, timeout=0.02)#открываем COM12 (нумерация портов начинается с 0)
    #COM = MySerial.ComPort(0, 9600, timeout=1)#открываем COM1 (нумерация портов начинается с 0)
    #COM.rs485_mode = serial.rs485.RS485Settings(delay_before_rx=0.004)
except:
    raise Exception('Error openning port!')

COM.LoggingIsOn=True#включаем логирование в файл
print COM
print 'open', COM.isOpen()
COM.close()
#создаем устройство
#owenDev=Owen.Owen(None,16);#тестовые данные
owenDev=Owen.OwenDevice(COM,16);#настоящий порт
count = 0
#owenDev.Debug=True#включем отладочные сообщения
while True:
    try:
        print '---------------------------------'
        print time.localtime()
        if not COM.isOpen():
            COM.open()
            print u'порт открыт'
        #Имя устройства
        NS = owenDev.GetNetworkSettings()  # читаем сетевые настройки устройства

        print 'ns', NS

        State = owenDev.GetInt16('r.st')
        print 'st', State
        print 'pr', owenDev.owenProtocol

        Start = owenDev.GetChar('n.Err')
        print 'start', Start

        Exit = owenDev.GetChar('exit')
        print 'exit', Exit

        chkSensor = owenDev.GetInt16('iRD')
        print 'chkSensor', chkSensor
        devName = owenDev.GetDeviceName()
        print 'Device name: {}'.format(devName)
        #Прошивка
        result = owenDev.GetFirmwareVersion()
        print 'Firmware version: {}'.format(result)
        #Только для ТРМ251
        if devName == 'TPM251':
            result = owenDev.GetIEEE32('r.oUt')
            print 'Output power: {}'.format(result)
        #считаем хэш параметра rEAd
        hashREAD=owenDev.GetHash('rEAd')
        #читаем с базового адреса
        result=owenDev.GetIEEE32(hashREAD,0,withTime=True)
        #можно и так
        result1=owenDev.GetIEEE32('rEAd',0,withTime=True)['value']
        #пример обработки исколЮчения, анализирует ошибку обрыв термопары
        try:
            #читаем с адреса базовый+1
            result2=owenDev.GetIEEE32(hashREAD,0,withTime=True)
        except Owen.OwenUnpackError as e:
            #обрабатываем ошибку раскодировки данных
            result2 = None
            if len(e.data) == 1:
                #это код ошибки
                if ord(e.data[0]) == 0xfd:
                    print u'Обрыв датчика'
                elif ord(e.data[0])==0xff:
                    print u'Некорректный калибровочный коэффициент'
                elif ord(e.data[0])==0xfb:
                    print u'Измеренное значение слишком мало'
                elif ord(e.data[0]) == 0xfa:
                    print u'Измеренное значение слишком велико'
                elif ord(e.data[0]) == 0xf7:
                    print u'Датчик отключен'
                elif ord(e.data[0]) == 0xf6:
                    print u'Данные не готовы'
                elif ord(e.data[0]) == 0xf0:
                    print u'Значение заведомо неверно'
            else:
                #бросаем исклЮчение дальше
                raise 'Owen device::Error when getting value!'
        except:
            #бросаем исклЮчение дальше
            raise 'Owen device::Error when getting value!'
        print 'Response from base address: ',result
        print 'Response from base address: ',result1
        print 'Response error: ',result2
        if COM.isOpen():
            COM.close()
            print u'порт закрыт'
        time.sleep(5)
    except Owen.OwenProtocolError:
        count +=1
        print '----COUNT--', count