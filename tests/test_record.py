# import unittest
# import time
# import numpy as np
# import logging
# from audioio import Audioio
# logging.basicConfig(level=logging.INFO)

# class TestRecord(unittest.TestCase):
#     """Test Recording"""

#     def setUp(self):
#         self.aio = Audioio(sr=44100, bs=256)

#     def tearDown(self):
#         pass

#     def test_stream_open(self):
#         """test recording """
#         self.aio.record(gain=[0.5])   # Need a better way to validate
#         self.assertTrue(self.aio.rec_stream.is_active(), True)
#         # check gain update
#         self.assertEqual(self.aio.in_gains, [0.5])

#     def test_block_mode(self):
#         # Block mode recording.:
#         self.aio.record(dur=1., block=True)
#         output = np.array(self.aio.record_buffer).flatten()
#         # recording result should be np.float32
#         self.assertEqual(output.dtype, 'float32')
#         # record length should be correct
#         self.assertAlmostEqual(output.shape[0]/self.aio.in_chan/self.aio.sr, 1., places=2)

#     def test_nonblock_mode(self):
#         self.aio.record(monitor=True)
#         time.sleep(2)
#         self.assertTrue(self.aio.rec_stream.is_active(), True)
#         self.aio.stop()
#         with self.assertRaises(OSError):
#             # Stream is not open, should throw OSError
#             test = self.aio.rec_stream.is_active()
