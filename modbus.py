# -*- coding: utf-8 -*-
import minimalmodbus, time, datetime
minimalmodbus.CLOSE_PORT_AFTER_EACH_CALL = True
#print minimalmodbus._getDiagnosticString()

import numpy as np

def signme(me):
    if me < 0x8000:
        return float(me)
    else:
        me = me - 0x10000
        return float(me)

error_buffer = ['','','','','']

def s_log(a):
    error_buffer.append(a)
    error_buffer.pop(1)

instrument = minimalmodbus.Instrument('/dev/ttyUSB0',slaveaddress=16, mode='rtu') # port name, slave address (in decimal)
instrument.debug = False
instrument.serial.baudrate = 57600
temperature=0
error=0
print instrument



counter = 0
counter2 = 0
temp_array = np.array([[0.0, 0],
                        [0.0, 0],
                        [0.0, 0],
                        [0.0, 0],
                        [0.0, 0],
                        [0.0, 0],
                        [0.0, 0]])

while True:
    a = datetime.datetime.now()
    s = time.localtime()
    Ch = 1
    while Ch <= 6:
        try:
            terr = temp_array[Ch][0]

            result = instrument.read_registers(1+6*(Ch-1), numberOfRegisters = 2)
            temp_array[Ch][0] = signme(result[0])/10
            temp_array[Ch][1] = result[1]
            print 'Ch', Ch, 'res:', temp_array[Ch][0], temp_array[Ch][1]

            if temp_array[Ch][1] > 0:
                print u'Ошибка измерения на канале ', Ch
                err = temp_array[Ch][1]
                temp_array[Ch][1] = int(1)
                temp_array[Ch][0] = terr
                # это код ошибки
                if err == 0xf00d:
                    print (u'Обрыв датчика, канал: ' + str(Ch) + ' ' + str(s.tm_hour) + ':' + str(
                        s.tm_min) + ':' + str(s.tm_sec))
                    s_log(u'Обрыв датчика, канал: ' + str(Ch) + ' ' + str(s.tm_hour) + ':' + str(
                        s.tm_min) + ':' + str(s.tm_sec))
                elif err == 0xf00f:
                    print (u'Некорректный калибровочный коэффициент, канал: ' + str(Ch) + ' ' + str(
                        s.tm_hour) + ':' + str(s.tm_min) + ':' + str(s.tm_sec))
                    s_log(u'Некорректный калибровочный коэффициент, канал: ' + str(Ch) + ' ' + str(
                        s.tm_hour) + ':' + str(s.tm_min) + ':' + str(s.tm_sec))
                elif err == 0xf00b:
                    print (u'Измеренное значение слишком мало, канал: ' + str(Ch) + ' ' + str(
                        s.tm_hour) + ':' + str(s.tm_min) + ':' + str(s.tm_sec))
                    s_log(u'Измеренное значение слишком мало, канал: ' + str(Ch) + ' ' + str(
                        s.tm_hour) + ':' + str(s.tm_min) + ':' + str(s.tm_sec))
                elif err == 0xf00a:
                    print (u'Измеренное значение слишком велико, канал: ' + str(Ch) + ' ' + str(
                        s.tm_hour) + ':' + str(s.tm_min) + ':' + str(s.tm_sec))
                    s_log(u'Измеренное значение слишком велико, канал: ' + str(Ch) + ' ' + str(
                        s.tm_hour) + ':' + str(s.tm_min) + ':' + str(s.tm_sec))
                elif err == 0xf007:
                    print (u'Датчик отключен, канал: ' + str(Ch) + ' ' + str(
                        s.tm_hour) + ':' + str(s.tm_min) + ':' + str(s.tm_sec))
                    s_log(u'Датчик отключен, канал: ' + str(Ch) + ' ' + str(
                        s.tm_hour) + ':' + str(s.tm_min) + ':' + str(s.tm_sec))
                elif err == 0xf006:
                    print (u'Данные температуры не готовы ' + str(Ch) + ' ' + str(
                        s.tm_hour) + ':' + str(s.tm_min) + ':' + str(s.tm_sec))
                    s_log(u'Данные температуры не готовы ' + str(Ch) + ' ' + str(
                        s.tm_hour) + ':' + str(s.tm_min) + ':' + str(s.tm_sec))
                elif err == 0xf000:
                    print (u'Значение заведомо неверно, канал: ' + str(Ch) + ' ' + str(
                        s.tm_hour) + ':' + str(s.tm_min) + ':' + str(s.tm_sec))
                    s_log(u'Значение заведомо неверно, канал: ' + str(Ch) + ' ' + str(
                        s.tm_hour) + ':' + str(s.tm_min) + ':' + str(s.tm_sec))

        except ValueError or TypeError or IOError:
            temp_array[Ch][1] = int(1)
            temp_array[Ch][0] = terr
            print u'Модуль ввода:: проблемы с ответом, канал: ' + str(Ch)
            s_log(u'Модуль ввода:: проблемы с ответом, канал: ' + str(Ch) + ' ' + str(
                s.tm_hour) + ':' + str(s.tm_min) + ':' + str(s.tm_sec))
            counter += 1

        #print temp_array[Ch]
        Ch += 1
    print '-------------------', str(s.tm_hour), ':', str(s.tm_min), ':', str(s.tm_sec), '-------------------'
    counter2 += 1
    eline = u'Ошибки = ' + str(counter) + u', ' + u'Вызовы = ' + str(counter2)
    error_buffer[0] = eline
    print error_buffer[0]
    sleepparam = float(str(datetime.datetime.now() - a)[-6:]) / 1000000
    print '-------------------', sleepparam, '-------------------'
    time.sleep(1 - sleepparam)