"""This file is to be used for development only, delete once done"""

import numpy as np
import time 
from audioio.core import Audioio

aio = Audioio(sr=44100, bs=256)
aio.info()