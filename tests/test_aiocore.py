# Test core parts
import unittest
from src.audioio import Aiocore
import logging
logging.basicConfig(level=logging.WARNING)


class Test_Core(unittest.TestCase):
    """Test App class in gui"""

    def setUp(self):
        self.aio = Aiocore()

    def test_dtype(self):
        """dtype is a property and unchangable"""
        self.assertEqual("float32", self.aio.dtype)
        try:
            self.aio.dtype = "float64"
        except AttributeError:
            print("test_code -> test_dtype: dtyp has no setter. Not supposed to...")

    def test_current_info(self):
        # Give info about the device
        info = self.aio.info
        print(info)

    def test_access_audio_devices(self):
        """Check default audio device"""
        self.aio.get_devices()

