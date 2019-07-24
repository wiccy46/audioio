import time
import numpy as np
import matplotlib.pyplot as plt
import logging
from audioio import Audioio
logging.basicConfig(level=logging.INFO)

aio = Audioio(sr=44100, bs=256)
# print(aio.get_devices())
aio.record(gain=0.5, block=True, dur=1.)
# time.sleep(3)

output = np.array(aio.record_buffer)

# print(output.shape)


# # for i in range(len(output)):
# #     if abs(output[i]) > 2.1e-10:
# #         print("First Onset found at ", i)
# #         break

# plt.plot(output)
# plt.show()