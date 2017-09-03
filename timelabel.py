# -*- coding: utf-8 -*-
import time, datetime, calendar
from PyQt4 import QtCore
#--------------temp measure-----------------------
class TimeThread(QtCore.QThread): # time label
    def __init__(self, time_signal, parent=None):
        super(TimeThread, self).__init__(parent)
        self.time_signal = time_signal
        self.isRun=False

    def run(self):
        while self.isRun:
            s=time.localtime()
            a = datetime.datetime.now()
            if s.tm_min<10:
                minutes='0'+str(s.tm_min)
            else:
                minutes=str(s.tm_min)
                
            if s.tm_hour<10:
                hours='0'+str(s.tm_hour)
            else:
                hours=str(s.tm_hour)
                
            if s.tm_sec<10:
                secundes='0'+str(s.tm_sec)
            else:
                secundes=str(s.tm_sec)
            
            month=_fromUtf8(calendar.month_name[s.tm_mon])
            day=str(s.tm_mday)
            dayname=_fromUtf8(calendar.day_name[s.tm_wday])
            out=['','','']
            
            out[0]=day+', ' + month
            out[1]='%s:%s:%s' % (hours,minutes,secundes)
            out[2]=dayname
            
            
            self.time_signal.emit(out)

            sleepparam = float(str(datetime.datetime.now()-a)[-6:])/1000000
            #print 1 - sleepparam
            time.sleep(1 - sleepparam)

    def stop(self):
        self.isRun=False
        
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s