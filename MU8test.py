# -*- coding: utf8 -*-

from TOwen import Owen
from TSystem import MySerial
import time
import minimalmodbus
minimalmodbus.CLOSE_PORT_AFTER_EACH_CALL = True
#Owen.test()#прогоняем тест библиотеки

#создаем последовательный порт
try:
    COM = MySerial.ComPort('/dev/ttyUSB0', 57600, timeout=0.05)
except:
    raise Exception('Error openning port!')

COM.LoggingIsOn=True#включаем логирование в файл
print COM

instrument = minimalmodbus.Instrument('/dev/ttyUSB0',slaveaddress=8, mode='rtu') # port name, slave address (in decimal)
instrument.debug = False
instrument.serial.baudrate = 57600


instrument.write_register(32, 5)
instrument.write_register(33, 5)

print instrument.read_registers(32,2)

instrument.write_register(0, 0)
instrument.write_register(1, 0)


#создаем устройство
#owenDev=Owen.Owen(None,16);#тестовые данные
owenDev=Owen.OwenDevice(COM,8);#настоящий порт
count = 0

devName = owenDev.GetDeviceName()
print 'Device name: {}'.format(devName)

# Прошивка
result = owenDev.GetFirmwareVersion()
print 'Firmware version: {}'.format(result)
#owenDev.Debug=True#включем отладочные сообщения
c=0
while True:
    try:
        #print '---------------------------------'
        #print time.localtime()
        # #Имя устройства
        # NS = owenDev.GetNetworkSettings()  # читаем сетевые настройки устройства
        #
        # print 'ns', NS
        #
        # State = owenDev.GetInt16('r.st')
        # print 'st', State
        # print 'pr', owenDev.owenProtocol
        #
        # Start = owenDev.GetChar('n.Err')
        # print 'start', Start
        #
        # Exit = owenDev.GetChar('exit')
        # print 'exit', Exit
        #
        # chkSensor = owenDev.GetInt16('iRD')
        # print 'chkSensor', chkSensor


        roe = (owenDev.GetFloat24('r.OE',  0), owenDev.GetFloat24('r.OE',  1))
        print 'roe=', roe[0], 'roe=', roe[1]

        print 'resOfWrite=', round(owenDev.writeFloat24('r.OE', 0, value=c), 3)
        # if c < 0.9:
        #     c+=0.1
        # else:
        #     c=0

        print 'addr=', owenDev.GetInt16(0x9F62, addrOffset = 0, withTime = False, withIndex = False)


        time.sleep(1)
    except Owen.OwenProtocolError:
        try:
            roe = (owenDev.GetFloat24('r.OE',  0), owenDev.GetFloat24('r.OE',  1))
            print 'roe=', roe[0], 'roe=', roe[1]

            time.sleep(1)
        except Owen.OwenProtocolError:
            count +=1
            print '----COUNT--', count