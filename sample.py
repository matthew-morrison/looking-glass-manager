# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import QApplication, QWidget

"""
using pyqt5-5.8.2, sip-4.19.2, 

"""

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    w = QWidget()
    w.resize(250,150)
    w.move(300,300)
    w.setWindowTitle('Simple')
    w.show()
    
    
    sys.exit(app.exec_())
