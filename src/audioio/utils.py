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
