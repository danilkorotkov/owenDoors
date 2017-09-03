#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys

# import PyQt4 QtCore and QtGui modules
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import os
os.environ["DISPLAY"] = ":0" #remote a

from mainwindow import MainWindow

if __name__ == '__main__':

    # create application
    app = QApplication( sys.argv )
    app.setApplicationName( 'owen control' )

    # create widget
    window = MainWindow()
    #window.show()
    window.showFullScreen()  

    # connection
    QObject.connect( app, SIGNAL( 'lastWindowClosed()' ), app, SLOT( 'quit()' ) )

    # execute application
    #sys.exit( app.exec_() )
    app.exec_()
    app.deleteLater()
    sys.exit()    
