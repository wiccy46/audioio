import unittest
import numpy as np
import logging
from audioio import Audioio
logging.basicConfig(level=logging.INFO)

class TestRecord(unittest.TestCase):
    """Test Recording"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_stream_open(self):
        """test recording """
        aio = Audioio(sr=44100, bs=256)

        # Check if stream is open
        # 1 Check stream open
        aio.record(gain=[0.5])   # Need a better way to validate
        self.assertTrue(aio.rec_stream.is_active(), True)
        # check gain update
        self.assertEqual(aio.in_gains, [0.5])

    def test_block_mode(self):
        aio = Audioio(sr=44100, bs=256)
        # Block mode recording.:
        aio.record(dur=1., block=True)
        output = np.array(aio.record_buffer).flatten()
        # recording result should be np.float32
        self.assertEqual(output.dtype, 'float32')
        # record length should be correct
        self.assertAlmostEqual(output.shape[0]/aio.in_chan/aio.sr, 1., places=2)



