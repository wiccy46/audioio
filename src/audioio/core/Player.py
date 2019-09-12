import numpy as np
import pyaudio
from .Core import Aiocore


class Player(Aiocore):
    """Player class"""
    def __init__(self, sr=44100, bs=1024, device_indices=(None, None)):
        super().__init__()
        
    def play(self):
        print("play audio")
    
    def stop(self):
        """Stop audio whenever"""
        pass
        