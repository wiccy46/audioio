from audioio.core import Audioio
import numpy as np
import matplotlib.pyplot as plt
import time
import logging
logging.basicConfig(level=logging.INFO)


aio = Audioio(sr=44100, bs=256)

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

aio.record(dur=3, block=True)   # Need a better way to validate

# print(aio.rec_stream.get_input_latency())
# print(aio.rec_stream.get_output_latency())
# print("Stream status: ", aio.rec_stream.is_active())

# print(aio.test_time)

output = np.array(aio.record_buffer).flatten()


# for i in range(len(output)):
#     if abs(output[i]) > 2.1e-10:
#         print("First Onset found at ", i)
#         break

plt.plot(output)
plt.show()
