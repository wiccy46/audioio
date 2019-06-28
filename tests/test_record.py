import unittest
from audioio.core import Audioio
import time
import matplotlib.pyplot as plt
import numpy as np

class TestRecord(unittest.TestCase):
    """Test Recording"""

    def setUp(self):
        pass

    def tearDown(self):
        pass


    def test_recording(self):
        """test recording """
        aio = Audioio(sr=44100, chunk=256)

        # Check if stream is open

        """
            How to validate recording works, 
            1. stream is open 
            2. status is at paContinue
            3. Sound is coming out 
            4. Audio gain is applied successfully 
            5. Record data in correct dimension 
            6. Output data in correct format (bytes) 
            7. There is a coorect amount of data after recording. 
        """

        aio.record(dur=3.0)   # Need a better way to validate
        self.assertTrue(aio.rec_stream.is_active(), True)
        # print("Stream status: ", aio.rec_stream.is_active())
        time.sleep(3.0)
        output = np.array(aio.record_buffer).flatten()

        for i in range(len(output)):
            if abs(output[i]) > 2.1e-10:
                print("First Onset found at ", i)
                break

        plt.plot(output)
        plt.show()


