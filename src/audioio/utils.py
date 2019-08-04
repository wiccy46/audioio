import numpy as np
import time 

def layout_add(layout, items):
    """Add widget or layout to layout. """
    for i in items:
        try:
            layout.addWidget(i)
        except:
            layout.addLayout(i)
    return layout

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


def decode(in_data, channels):
    """
    Convert a byte stream into a 2D numpy array with 
    shape (chunk_size, channels)

    Samples are interleaved, so for a stereo stream with left channel 
    of [L0, L1, L2, ...] and right channel of [R0, R1, R2, ...], the output 
    is ordered as [L0, R0, L1, R1, ...]
    """
    # TODO: handle data type as parameter, convert between pyaudio/numpy types
    result = np.fromstring(in_data, dtype=np.float32)
    chunk_length = len(result) // channels
    result = np.reshape(result, (chunk_length, channels))
    return result


def encode(signal):
    """
    Convert a 2D numpy array into a byte stream for PyAudio

    Signal should be a numpy array with shape (chunk_size, channels)
    """
    interleaved = signal.flatten()
    out_data = interleaved.astype(np.float32).tostring()
    return out_data