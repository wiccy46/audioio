import numpy as np
import pyaudio
import logging
import time

_LOGGER = logging.getLogger(__name__)
_LOGGER.addHandler(logging.NullHandler())

class BasicAudioio(object):
    """Core class of the audioio, currently only dealing with float32, later to add more dtype in, such as int16

    Args:
      sr (int): sampling rate
      bs (int): bs size or buffer size
      pa (PyAudio()): pyaudio class for audio streaming


    TODO: make sure everytime a new device is set, the parameters are updated.
    """

    def __init__(self, sr=44100, bs=1024, in_device=None, out_device=None):
        self.sr = sr
        self.bs = bs
        self.pa = pyaudio.PyAudio()
        self._dtype = "float32"
        # Get all audio input and output
        self.input_list = []
        self.output_list = []
        for i in range(self.pa.get_device_count()):
            if self.pa.get_device_info_by_index(i)['maxInputChannels'] > 0:
                self.input_list.append(self.pa.get_device_info_by_index(i))
            if self.pa.get_device_info_by_index(i)['maxOutputChannels'] > 0:
                self.output_list.append(self.pa.get_device_info_by_index(i))

        self.in_gains = [1.]  # needs to be scaled based on the channels
        self.out_gains = [1.]
        self.record_buffer = []  # A buffer for long audio being recorded in.

        if in_device is None:
            self.in_idx = self.pa.get_default_input_device_info()['index']
        else:
            self.in_idx = in_device

        if out_device is None:
            self.out_idx = self.pa.get_default_output_device_info()['index']
        else:
            self.out_idx = out_device
        self.test_time = []


    @property
    def dtype(self):
        return self._dtype

    @property
    def in_idx(self):
        # Input index
        return self._in_idx

    @in_idx.setter
    def in_idx(self, val):
        self._in_idx = val
        self._in_dict = self.pa.get_device_info_by_index(self.in_idx)
        self._in_chan = self._in_dict['maxInputChannels'] 

    @property
    def in_chan(self):
        # Input channels
        return self._in_chan

    @property
    def out_idx(self):
        # Output index
        return self._out_idx

    @out_idx.setter
    def out_idx(self, val):
        self._out_idx = val
        self._out_dict = self.pa.get_device_info_by_index(self.out_idx)
        self._out_chan = self._out_dict['maxOutputChannels']

    @property
    def out_chan(self):
        # Output channels 
        return self._out_chan

    @out_chan.setter
    def out_chan(self, val):
        self._out_idx = val

    @property
    def in_dict(self):
        return self._in_dict

    @property
    def out_dict(self):
        return self._out_dict

    def info(self):
        """Print all necessary information about the class"""

        msg = f"""Audioio: sr={self.sr}, bs={self.bs}, \n 
                Input: {self.in_dict['name']}, index: {self.in_dict['index']}, channels: {self.in_dict['maxInputChannels']}, \n 
                Output: {self.out_dict['name']}, index: {self.out_dict['index']}, channels: {self.out_dict['maxOutputChannels']}"""
        print(msg)

    def get_devices(self, item="all"):
        """Print audio all available devices"""
        if item == "all":
            for i in range(self.pa.get_device_count()):
                print(self.pa.get_device_info_by_index(i))
        else:
            for i in range(self.pa.get_device_count()):
                print(self.pa.get_device_info_by_index(i)[item])

    def set_device(self, in_device=-1, out_device=-1):
        """Set the input and output device. The default argument is -1 meaning not change."""
        if isinstance(in_device, int) and in_device > -1:
            self.in_idx = in_device
        elif in_device == 'default' or in_device == 'Default':
            self.in_idx = self.pa.get_default_input_device_info()['index']
            
        if isinstance(out_device, int) and out_device > -1:
            self.out_idx = out_device
        elif out_device == 'default' or out_device == 'Default':
            self.out_idx = self.pa.get_default_output_device_info()['index']

