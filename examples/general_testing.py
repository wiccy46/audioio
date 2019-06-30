"""This file is to be used for development only, delete once done"""

import numpy as np
import time 

def dbamp(db):
    """Convert db to amplitude

    Args:
        db (list) -- decibel

    Returns:
        (list) -- [description]
    """

    for i in range(len(db)):
        db[i] = 10 ** (db[i] / 20.0)


    return db

a = [1.0, 0.5, 2., 4, 2, 3, 4, ]

for i in range(5):
    dbamp(a)

