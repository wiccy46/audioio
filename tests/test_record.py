import unittest
import time
import numpy as np
import logging
from src.audioio.core import Recorder
logging.basicConfig(level=logging.INFO)

class Test_Record(unittest.TestCase):
    """Test Recording"""

    def setUp(self):
        """test recording """
        self.recorder = Recorder(sr=44100, bs=256)

    def tearDown(self):
        pass
    
    def test_import(self):
        """Make sure importing Recorder from audioio or audioio.core are both ok"""
        from src.audioio.core import Recorder
        self.recorder = Recorder(sr=44100, bs=256)
        self.assertEqual(self.sr, 44100)
        from src.audioio import Recorder
        self.recorder = Recorder(sr=44100, bs=256)
        self.assertEqual(self.sr, 44100)

    def test_stream_open(self):
        """Make sure stream can be opened"""
        self.recorder.record(gain=[0.5])   # Need a better way to validate
        self.assertTrue(self.recorder.record_stream.is_active(), True)
        self.assertEqual(self.recorder.input_gains, [0.5])

    def test_block_mode(self):
        """Block mode recording."""
        self.recorder.record(dur=1., block=True)
        output = np.array(self.recorder.record_buffer).flatten()
        # recording result should be np.float32
        self.assertEqual(output.dtype, 'float32')
        # record length should be correct
        self.assertAlmostEqual(
            output.shape[0] / self.recorder.input_channels 
            / self.recorder.sr, 1., places=2)

    def test_nonblock_mode(self):
        """Non blocking Mode recording"""
        self.recorder.record(monitor=True)
        time.sleep(2)
        self.assertTrue(
            self.recorder.record_stream.is_active(), True)
        self.recorder.stop()
        with self.assertRaises(OSError):
            # Stream is not open, should throw OSError
            test = self.recorder.record_stream.is_active()
