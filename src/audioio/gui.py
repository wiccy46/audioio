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
        # Create the main layouts. left for in/out, right for dropsdown + master. 
        self.main_layout = QHBoxLayout()
        self.left_layout = QVBoxLayout()
        self.right_layout = QVBoxLayout()
        # Create groups. 
        self.make_util_group()
        self.left_layout.addWidget(self.device_group)
        self.main_layout.addLayout(self.left_layout)
        self.win.setCentralWidget(QWidget(self.win))
        self.win.centralWidget().setLayout(self.main_layout)
        self.win.show()
        sys.exit(self.app.exec_()) 
        
    def make_util_group(self):
        self.device_group = QGroupBox("")
        util_group_layout = QVBoxLayout()
        self.input_dropdown = QComboBox()
        self.input_dropdown.activated[str].connect(self.change_input)
        inItem = []
        for i in self.il:
            inItem.append(i["name"] + " " + str(i['maxInputChannels']))
        self.input_dropdown.addItems(inItem)
        self.input_label = QLabel("Input")
        self.output_label = QLabel("Output")
        self.output_dropdown = QComboBox()
        outItem = []
        for i in self.ol:
            outItem.append(i["name"] + " " + str(i['maxOutputChannels']))
        self.output_dropdown.addItems(outItem)
        self.output_dropdown.activated[str].connect(self.change_output)
        sr_layout = QHBoxLayout()
        sr_label = QLabel("Sampling Rate")
        self.sr_edit = QLineEdit()
        self.sr_edit.setText(str(self.sr))
        sr_layout.addWidget(sr_label)
        sr_layout.addWidget(self.sr_edit)
        bs_layout = QHBoxLayout()
        bs_label = QLabel("Buffer Size")
        self.bs_edit = QLineEdit()
        self.bs_edit.setText(str(self.bs))
        bs_layout.addWidget(bs_label)
        bs_layout.addWidget(self.bs_edit)
        util_group_layout = self._add_widget(util_group_layout, [self.input_label, self.input_dropdown,
                                              self.output_label, self.output_dropdown])
        util_group_layout.addLayout(sr_layout)
        util_group_layout.addLayout(bs_layout)
        self.device_group.setLayout(util_group_layout)
        _LOGGER.debug("Created utility group")
        
    def _add_widget(self, layout, widgets):
        """Add widgets to layout, take layout and give widgets as list to layout. Then return"""
        for w in widgets:
            layout.addWidget(w)
        return layout
    
    def change_input(self, text):
        """Change the input device based on name"""
        # This is not very efficient. 
        _LOGGER.info("Input dropdown activate")
        for i in range(len(self.il)):
            if self.il[i]['name'] in text:
                self.in_idx = self.il[i]['index']
                
    def change_output(self, text):
        """Change the output device based on name"""
        _LOGGER.info("Output dropdown activate")
        for i in range(len(self.ol)):
            if self.ol[i]['name'] in text:
                self.output_idx = self.ol[i]['index']
                # Need to update the channels 