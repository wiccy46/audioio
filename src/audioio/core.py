import numpy as np
import pyaudio


class Audioio():
    """Core class of the audioio

    Args:
      n (int): integer

    """

    def __init__(self, sr=44100):
        self.sr = sr

