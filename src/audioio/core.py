import numpy as np
import pyaudio


class Audioio():
    """Core class of the audioio, currently only dealing with float32, later to add more dtype in, such as int16

    Args:
      sr (int): sampling rate
      chunk (int): chunk size or buffer size
      pa (PyAudio()): pyaudio class for audio streaming

    """

    def __init__(self, sr=44100, chunk=256):
        self.sr = sr
        self.chunk = chunk
        self.pa = pyaudio.PyAudio()
        self._dtype = "float32"
        # Get all audio input and output
        self.il = []
        self.ol = []
        for i in range(self.pa.get_device_count()):
            if self.pa.get_device_info_by_index(i)['maxInputChannels'] > 0:
                self.il.append(self.pa.get_device_info_by_index(i))
            if self.pa.get_device_info_by_index(i)['maxOutputChannels'] > 0:
                self.ol.append(self.pa.get_device_info_by_index(i))

    @property
    def dtype(self):
        return self._dtype

    def get_device(self):
        """Print audio all available devices"""
        for i in range(self.pa.get_device_count()):
            print(self.pa.get_device_info_by_index(i))

    def set_device(self, input=0, output=1):
        # check how to set default devices.
        pass

    def _play_callback(self, in_data, frame_count, time_info, flag):
        """Audio callback when stream is open. This is only used for playing, not for recording.

        Args:
          in_data (bytes): audio inputs per frame/chunk
          frame_count (int): counting the frame

        Returns:
          out_data (TBD): output data per frame
          status (paStatus): paContinute or paComplete indicating whether the stream is on or not.
        """
        if (self.frameCount < self.total_chunk):
            out_data = self._outputgain(self.play_data[self.frameCount])
            self.frameCount += 1
            return out_data, pyaudio.paContinue
        else:  # The last one .
            out_data = bytes(np.zeros(self.chunk * self.output_channels))
            return out_data, pyaudio.paComplete