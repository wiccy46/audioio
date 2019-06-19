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
