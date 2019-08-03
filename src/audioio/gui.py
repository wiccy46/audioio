import time, sys, threading
import logging
import numpy as np
from . import Audioio
from .utils import decode, encode


_LOGGER = logging.getLogger(__name__)
_LOGGER.addHandler(logging.NullHandler())
try:
    from PyQt5.QtGui import *
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget
except ImportError:
    _LOGGER.error("audioio.gui requires PyQt5 to work. It couldn't import PyQt5.")

from PyQt5.Qt import PYQT_VERSION_STR  # This is only for testing. 


# class Gui(Audioio):
#     def __init__(self, link=None):  # Use link to link with the aio class. 
#         if link is None:
#             # create a new aio
#             pass
#         else:
#             if isinstance(aio, Audioio):
#                 self.aio = aio
#             else:
#                 # print("Got error msg")
#                 msg = "aio argument needs to be an Audioio object,"
#                 " or None which will create a new Audioio obejct."
#                 raise TypeError(msg)
#     def checkqt(self):
#         print("PyQt5 version: " + PYQT_VERSION_STR)

class Console(Audioio):
    def __init__(self, size=(600, 400), pos=(500, 500),
         sr=44100, bs=1024, device=[None, None]):
        """Init a gui console for audio recording and routing. """
        super(Console, self).__init__(sr=sr, bs=bs, device=device)
        self.app = QApplication(sys.argv)
        self.max_width = QDesktopWidget().screenGeometry().width()
        self.max_height = QDesktopWidget().screenGeometry().height()
        self.win = QMainWindow()
        self.win.move(pos[0], pos[1])
        self.win.resize(size[0], size[1])
        self.win.setWindowTitle('Console')
        self.main_layout = QVBoxLayout()
        self.left_layout = QHBoxLayout()
        self.right_layout = QHBoxLayout()
        
        
        
        self.win.setCentralWidget(QWidget(self.win))
        self.win.centralWidget().setLayout(self.main_layout)
        
        
        
        self.win.show()
        sys.exit(self.app.exec_()) 
    