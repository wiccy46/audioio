import unittest
from audioio.core import Audioio
import time
import matplotlib.pyplot as plt
import numpy as np
import logging
logging.basicConfig(level=logging.INFO)

class TestRecord(unittest.TestCase):
    """Test Recording"""

    def setUp(self):
        pass

    def tearDown(self):
        pass


    def test_recording(self):
        """test recording """
        aio = Audioio(sr=44100, bs=256)

        # Check if stream is open

        """
            How to validate recording works, 
            1. stream is open 
            3. Sound is coming out 
            4. Audio gain is applied successfully 
            5. Record data in correct dimension 
            6. Output data in correct format (bytes) 
            7. There is a coorect amount of data after recording. 
            7. Stream should be close after ward. 
        """

        # 1 Check stream open 
        aio.record()   # Need a better way to validate
        self.assertTrue(aio.rec_stream.is_active(), True)

        # 2. Block mode recording.:
        aio.record(dur=3, block=True)

        output = np.array(aio.record_buffer).flatten()

        for i in range(len(output)):
            if abs(output[i]) > 2.1e-10:
                print("First Onset found at ", i)
                break

        plt.plot(output)
        plt.show()


