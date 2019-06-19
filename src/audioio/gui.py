import time, sys, threading
import logging
import numpy as np

_LOGGER = logging.getLogger(__name__)
_LOGGER.addHandler(logging.NullHandler())
try:
    from PyQt5.QtGui import *
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import QMainWindow
except ImportError:
    _LOGGER.error("audioio.gui requires PyQt5 to work. It couldn't import PyQt5.")

from PyQt5.Qt import PYQT_VERSION_STR  # This is only for testing. 


class gui():
    def __init__(self, aio):
        self.aio = aio

    def checkqt(self):
        print(PYQT_VERSION_STR)
    