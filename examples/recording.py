import time
import numpy as np
import matplotlib.pyplot as plt
import logging
from audioio.core import Recorder

recorder = Recorder(sr=44100, bs=256)


recorder.record(monitor=True)
time.sleep(3)
print('Before stop. ')
recorder.stop()
signal_array = recorder.sig
plt.plot(signal_array)
plt.show()