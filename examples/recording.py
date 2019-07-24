import time
import numpy as np
import matplotlib.pyplot as plt
import logging
from audioio import Audioio
logging.basicConfig(level=logging.INFO)

aio = Audioio(sr=44100, bs=256)
# print(aio.get_devices())
# aio.record(gain=0.5, block=True, dur=1.)

aio.record(gain=[0.4, 0.2], monitor=True)
time.sleep(3)
print('Before stop. ')
aio.stop()
sig = aio.sig
plt.plot(sig)
plt.show()