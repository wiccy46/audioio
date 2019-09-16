"""core class of Audioio"""
import logging
import numpy as np
import pyaudio

_LOGGER = logging.getLogger(__name__)
_LOGGER.addHandler(logging.NullHandler())


class Aiocore(object):
    """Core class of the audioio, currently only dealing with float32,
    later to add more dtype in, such as int16.

    Attributes:
        sr : int
            Sampling rate
        bs : int
            Block size
        pa : pyaudio.PyAudio()
            Pyaudio object, for streaming audio
        dtype : float
            Const of audio data type, default to be 'float32' and currently noneditable
        input_index : int
    """

    def __init__(self, sr=44100, bs=1024, device_indices=(None, None)):
        """Aiocore init

        Parameters
        ----------
        sr : int
            Sampling rate
        bs : int
            Block size, aka buffer size
        device : tuple or list
            A tuple of input and output device index.
            By default None, which will opt for the device audio device.
        """
        self.sr = sr
        self.bs = bs
        self.pa = pyaudio.PyAudio()

        self._dtype = "float32"
        self._input_index = 0
        self._output_index = 1
        self._input_channels = 0
        self._output_channels = 0
        self.input_gains = [1.]  # needs to be scaled based on the channels
        self.output_gains = [1.]

        # TODO check whether this complie to the output channels.
        # TODO Or maybe broadcast it to the correct output channels.
        self.silence = np.zeros((self.bs, 1), dtype=self.dtype)
        self.input_index = device_indices[0]
        self.output_index = device_indices[1]
        self.test_time = []  # Currently not used.

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
        return self._dtype

    @property
    def input_index(self):
        # Input index
        return self._input_index

    @input_index.setter
    def input_index(self, val):
        print(val)
        self._input_index = self.pa.get_default_input_device_info()['index'] if val is None else val
        self._input_channels = self.pa.get_device_info_by_index(self.input_index)['maxInputChannels']

    @property
    def input_channels(self):
        return self._input_channels

    @property
    def output_index(self):
        return self._output_index

    @output_index.setter
    def output_index(self, val):
        self._output_index = self.pa.get_default_output_device_info()['index'] if val is None else val
        self._output_channels = self.pa.get_device_info_by_index(self.output_index)['maxOutputChannels']

    @property
    def output_channels(self):
        return self._output_channels

    @property
    def info(self):
        """Print info about the current Input and Output devices."""
        in_dict = self.pa.get_device_info_by_index(self.input_index)
        out_dict = self.pa.get_device_info_by_index(self.output_index)
        msg = f"""Audioio: sr={self.sr}, bs={self.bs},
Input: {in_dict['name']}, index: {in_dict['index']}, channels: {in_dict['maxInputChannels']},
Output: {out_dict['name']}, index: {out_dict['index']}, channels: {out_dict['maxOutputChannels']}."""
        return msg

    def get_devices(self, item="all"):
        """Get the info of all available audio devices as a list of string."""
        device_info = []
        if item == "all":
            for i in range(self.pa.get_device_count()):
                device_info.append(self.pa.get_device_info_by_index(i))
        else:
            for i in range(self.pa.get_device_count()):
                device_info.append(self.pa.get_device_info_by_index(i)[item])
        return device_info

    def set_devices(self, device=(None, None)):
        """Set inout device"""
        self.input_index = device[0]
        self.output_index = device[1]
