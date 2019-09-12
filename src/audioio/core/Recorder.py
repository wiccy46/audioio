import logging
from numbers import Number
import numpy as np 
import pyaudio
from .Core import Aiocore

_LOGGER = logging.getLogger(__name__)
_LOGGER.addHandler(logging.NullHandler())


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


class Recorder(Aiocore):
    def __init__(self, sr=44100, bs=1024, device_indices=(None, None)):
        super().__init__()
        self.record_buffer = []
    
    def clear_record_buffer(self):
        self.record_buffer = []  #TODO Consider using a fixed length for performance.
    
    def record(self, gain=1., dur=None, block=False, monitor=False):
        """Record audio

        Parameters
        ----------
        gain : float or list
            If float, apply the gain on all channel, if list apply to individual channel accordingly.
        dur : float or None
            Default is None, the recording is switched on definitely. If number, record a fixed duration in seconds
        block : bool
            Decide whether record block the process or not.
        monitor : bool
            Only available in non-blocking mode, allow directly monitoring as gained input will be sent to outputs.
            Be vary of the feedback.
        """
        try:
            # restarting recording without closing stream, resulting an unstoppable stream.
            # This can happen in Jupyter when you trigger record multple times without stopping it first.
            self.rec_stream.stop_stream()
            self.rec_stream.close()
            _LOGGER.info("record stream close. ")
        except AttributeError:
            _LOGGER.info("self.rec_stream not exsist.")
        _LOGGER.info(" Start Recording")
        
        self.record_buffer = []  # Clear the bufferlist for new recording.

        if isinstance(gain, list):
            self.input_gains = gain
        elif isinstance(gain, Number):
            self.input_gains = np.full(self.input_channels, gain)
        else:
            raise TypeError("Gain needs to be either list of float.")

        if dur is not None and block:
            self._block_mode_recording(dur)

        elif dur is None or not block:  # non blocking mode
            self.silence = np.zeros((self.bs, self.output_channels)) 
            callback = self._record_callback_monitor if monitor else self._record_callback
            self.rec_stream = self.pa.open(
                format=pyaudio.paFloat32,
                channels=self.output_channels,
                rate=self.sr,
                input=True,
                output=True,  
                input_device_index=self.input_index,
                output_device_index=self.output_index,
                frames_per_buffer=self.bs,        
                stream_callback=callback)
            self.rec_stream.start_stream()

    def _record_callback_monitor(self, in_data, frame_count, time_info, flag):
        """Callback for record stream"""
        signal = decode(in_data, self.input_channels) 
        signal *= self.input_gains
        #process 0- > find pitch 
        self.record_buffer.append(signal)
        # out = audio_data.astype(np.float32)  # At this stage it is finalized 
        return signal, pyaudio.paContinue   

    def _block_mode_recording(self, dur):
        _LOGGER.info(f" Block mode recording of {dur} seconds.")
        self.rec_dur = int(self.sr * dur)
        self.rec_stream = self.pa.open(
            format=pyaudio.paFloat32,
            channels=self.output_channels,
            rate=self.sr,
            input=True,
            output=True,  
            input_device_index=self.input_index,
            output_device_index=self.output_index,
            frames_per_buffer=self.bs)
        # Counting here. System is blocked in the foor loop. 
        for i in range(0, int(self.sr / self.bs * dur)):
            # Apply gain here. 
            signal = decode(self.rec_stream.read(self.bs), self.input_channels)
            signal *= self.input_gains  # Apply signal gain. 
            self.record_buffer.append(signal)
        self.rec_stream.stop_stream()
        self.rec_stream.close()
        _LOGGER.info(" Record Finished.")
    
    def _record_callback(self, in_data, frame_count, time_info, flag):
        """Callback for record stream"""
        signal = decode(in_data, self.input_channels) 
        signal *= self.input_gains  # Apply signal gain. 
        self.record_buffer.append(signal)
        return self.silence, pyaudio.paContinue
    
    def stop(self):
        """Stop recording"""
        try:
            self.rec_stream.stop_stream()
            self.rec_stream.close()
            _LOGGER.info("record stream close. ")
        except AttributeError:
            print("Attribute error")  
            _LOGGER.info("self.rec_stream not exsist.")
        