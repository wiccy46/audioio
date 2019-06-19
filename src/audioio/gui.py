from audioio.core import Audioio
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


class App():
    def __init__(self, aio=None):
        if aio is None:
            # create a new aio
            pass
        else:
            if isinstance(aio, Audioio):
                self.aio = aio
            else:
                # print("Got error msg")
                msg = "aio argument needs to be an Audioio object,"
                " or None which will create a new Audioio obejct."
                raise TypeError(msg)
    def checkqt(self):
        print("PyQt5 version: " + PYQT_VERSION_STR)
