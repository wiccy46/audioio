import time
import numpy as np
import matplotlib.pyplot as plt
import logging
from audioio.core import Audioio
logging.basicConfig(level=logging.INFO)

aio = Audioio(sr=44100, bs=256)

# Check if stream is open


# aio.record(dur=3, block=True)   # Need a better way to validate

# print(aio.rec_stream.get_input_latency())
# print(aio.rec_stream.get_output_latency())
# print("Stream status: ", aio.rec_stream.is_active())

# print(aio.test_time)

aio.record(gain=[0.5], block=False)
time.sleep(3)

output = np.array(aio.record_buffer)

print(output.shape)


# for i in range(len(output)):
#     if abs(output[i]) > 2.1e-10:
#         print("First Onset found at ", i)
#         break

plt.plot(output)
plt.show()
