import numpy as np
import pyaudio
import logging
import time

_LOGGER = logging.getLogger(__name__)
_LOGGER.addHandler(logging.NullHandler())

class Aiocore(object):
    """Core class of the audioio, currently only dealing with float32, later to add more dtype in, such as int16

    Attributes:
      sr (int): sampling rate
      bs (int): bs size or buffer size
      pa (PyAudio()): pyaudio class for audio streaming

    TODO: make sure everytime a new device is set, the parameters are updated.
    """

    def __init__(self, sr=44100, bs=1024, device=(None, None)):
        """Aiocore init
        
        Parameters
        ----------
        sr : int
            Sampling rate
        bs : int
            Block size, aka buffer size
        device : tuple or list
            A tuple of input and output device index. By default None, which will opt for the device audio device. 
        
        """
        self.sr = sr
        self.bs = bs
        self.pa = pyaudio.PyAudio()
        self._dtype = "float32"

        self.in_gains = [1.]  # needs to be scaled based on the channels
        self.out_gains = [1.]
        self.record_buffer = []  # A buffer for long audio being recorded in.

        self.empty_buffer = np.zeros((self.bs, 1), dtype=self._dtype)
        if device[0] is None:
            self.in_idx = self.pa.get_default_input_device_info()['index']
        else:
            self.in_idx = device[0]

        if device[1] is None:
            self.out_idx = self.pa.get_default_output_device_info()['index']
        else:
            self.out_idx = device[1]
        self.test_time = []

    @property
    def input_devices(self):
        """Return a dict of input devices and their info"""
        input_devices = []
        for i in range(self.pa.get_device_count()):
            if self.pa.get_device_info_by_index(i)['maxInputChannels'] > 0:
                input_devices.append(self.pa.get_device_info_by_index(i))
        return input_devices

    @property
    def output_devices(self):
        """Return a dict of input devices and their info"""
        output_devices = []
        for i in range(self.pa.get_device_count()):
            if self.pa.get_device_info_by_index(i)['maxOutputChannels'] > 0:
                output_devices.append(self.pa.get_device_info_by_index(i))
        return output_devices

    @property
    def dtype(self):
        """Audio data type, it only has a getter."""
        return self._dtype

    @property
    def in_idx(self):
        # Input index
        return self._in_idx

    @in_idx.setter
    def in_idx(self, val):
        self._in_idx = val
        self._in_chan = self.pa.get_device_info_by_index(self.in_idx)['maxInputChannels'] 

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
        self._out_chan = self.pa.get_device_info_by_index(self.out_idx)['maxOutputChannels']

    @property
    def out_chan(self):
        # Output channels 
        return self._out_chan

    @property
    def info(self):
        """Print all necessary information about the class"""
        in_dict = self.pa.get_device_info_by_index(self.in_idx)
        out_dict = self.pa.get_device_info_by_index(self.out_idx)
        msg = f"""Audioio: sr={self.sr}, bs={self.bs},
Input: {in_dict['name']}, index: {in_dict['index']}, channels: {in_dict['maxInputChannels']},
Output: {out_dict['name']}, index: {out_dict['index']}, channels: {out_dict['maxOutputChannels']}."""
        return msg

    def get_devices(self, item="all"):
        """Print all available devices"""
        device_info = []
        if item == "all":
            for i in range(self.pa.get_device_count()):
                # print(type(self.pa.get_device_info_by_index(i)))
                # print(self.pa.get_device_info_by_index(i))\
                device_info.append(self.pa.get_device_info_by_index(i))
        else:
            for i in range(self.pa.get_device_count()):
                # print(self.pa.get_device_info_by_index(i)[item])
                device_info.append(self.pa.get_device_info_by_index(i)[item])
        return device_info

    def set_device(self, device=[None, None]):
        """Set inout device"""
        if device[0] is None:
            self.in_idx = self.pa.get_default_input_device_info()['index']
        else:
            self.in_idx = device[0]
        if device[1] is None:
            self.out_idx = self.pa.get_default_output_device_info()['index']
        else:
            self.out_idx = device[1]
            