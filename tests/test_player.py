# Test core parts
import unittest
from src.audioio.core import Player
import logging
logging.basicConfig(level=logging.WARNING)


class Test_Player(unittest.TestCase):
    """Test App class in gui"""

    def setUp(self):
        self.player = Player()

    def test_dtype(self):
        """dtype is a property and unchangable"""
        self.assertEqual("float32", self.player.dtype)
        try:
            self.player.dtype = "float64"
        except AttributeError:
            print("test_code -> test_dtype: dtyp has no setter. Not supposed to...")

    def test_access_audio_devices(self):
        """Check default audio device"""
        self.player.get_devices()

    def test_info(self):
        # Give info about the device
        info = self.player.info
        print(info)