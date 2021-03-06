import unittest
from audioio.core import Audioio
import logging
logging.basicConfig(level=logging.WARNING)

class TestCore(unittest.TestCase):
    """Test App class in gui"""

    def setUp(self):
        self.aio = Audioio()


    def test_dtype(self):
        """dtype is a property and unchangable"""
        self.assertEqual("float32", self.aio.dtype)

        try:
            self.aio.dtype = "float64"
        except AttributeError:
            print("test_code -> test_dtype: dtyp has no setter. Not supposed to...")

    def test_access_audio_devices(self):
        self.aio.get_device()
        self.assertGreater(len(self.aio.il), 0)
        self.assertGreater(len(self.aio.ol), 0)
