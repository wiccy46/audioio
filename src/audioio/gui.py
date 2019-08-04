import time, sys, threading
import logging
import numpy as np
from . import Audioio
from .utils import decode, encode, layout_add
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
        input_label = QLabel("Input ")
        input_layout = QHBoxLayout()
        input_layout = layout_add(input_layout, [input_label, self.input_dropdown])
        
        output_label = QLabel("Output ")
        self.output_dropdown = QComboBox()
        out_item = []
        for i in self.ol:
            out_item.append(i["name"] + " " + str(i['maxOutputChannels']))
        self.output_dropdown.addItems(out_item)
        self.output_dropdown.activated[str].connect(self.change_output)
        output_layout = QHBoxLayout()
        output_layout = layout_add(output_layout, [output_label, self.output_dropdown])
        
        sr_layout = QHBoxLayout()
        sr_label = QLabel("Sampling Rate (Hz)")
        self.sr_edit = QComboBox()
        sr_l = [96000, 88200, 48000, 44100, 44100//2, 44100//3, 44100//4]
        sr_l = [str(x) for x in sr_l]
        self.sr_edit.addItems(sr_l)
        self.sr_edit.setCurrentIndex(3)
        self.sr_edit.activated[str].connect(self.change_sr)
        sr_layout.addWidget(sr_label)
        sr_layout.addWidget(self.sr_edit)
        
        bs_layout = QHBoxLayout()
        bs_label = QLabel("Buffer Size")
        self.bs_edit = QComboBox()
        bs_l = [2048 * 2, 2048, 1024, 512, 256, 128, 64, 32, 16, 8]
        bs_l = [str(x) for x in bs_l]
        self.bs_edit.addItems(bs_l)
        self.bs_edit.setCurrentIndex(2)
        self.bs_edit.activated[str].connect(self.change_bs)
        # self.bs_edit.setText(str(self.bs))
        bs_layout.addWidget(bs_label)
        bs_layout.addWidget(self.bs_edit)
        util_group_layout = layout_add(util_group_layout, [input_layout, output_layout, sr_layout, bs_layout])
        self.device_group.setLayout(util_group_layout)
        _LOGGER.debug("Created utility group")
    
    def change_input(self, text):
        """Change the input device based on name"""
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
                
    def change_sr(self, text):
        """Change sr"""
        _LOGGER.info("Sr dropdown activate")
        self.sr = int(text)
        
    def change_bs(self, text):
        """Change bs"""
        _LOGGER.info("bs dropdown activate")
        self.bs = int(text)    