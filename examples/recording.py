import time
import numpy as np
import matplotlib.pyplot as plt
import logging
from audioio import Audioio
logging.basicConfig(level=logging.INFO)

aio = Audioio(sr=44100, bs=256)
# print(aio.get_devices())
print(aio.sig)
aio.record(gain=0.5, block=True, dur=3.)
# time.sleep(3)

output = np.array(aio.record_buffer)

print(aio.sig)
# print(output.shape)


# # for i in range(len(output)):
# #     if abs(output[i]) > 2.1e-10:
# #         print("First Onset found at ", i)
# #         break

# plt.plot(output)
# plt.show()