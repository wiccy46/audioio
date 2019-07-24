# console.py
import logging
from warnings import warn
from numbers import Number
import pyaudio
import numpy as np 
from . import BasicAudioio
from .utils import decode, encode


_LOGGER = logging.getLogger(__name__)
_LOGGER.addHandler(logging.NullHandler())


class Audioio(BasicAudioio):
    def __init__(self, sr=44100, bs=1024, device=[None, None]):
        super(Audioio, self).__init__(sr=sr, bs=bs, device=device)
        self.silence = np.zeros((self.bs, self.out_chan))

    # Implement a signal property that only has a getter and return the audio signal. 
    @property
    def sig(self):
        if self.record_buffer == []:
            warn(" There is no signal recorded, return [].")
            return []
        else:
            # An alternate way is self.record_buffer.reshape(chunk*bs, chan)
            return np.concatenate(self.record_buffer, 0)

    def record(self, gain=1., dur=None, block=False, monitor=False):
        """Record audio

        Parameters
        ----------
        gain : float or list
            If float, apply the gain on all channel, if list apply to individual channel accordingly.
        dur : float, int or None
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
        # self.input_channels = self.pa.get_device_info_by_index(self.input_idx).get("maxInputChannels")
        if isinstance(gain, list):
            self.in_gains = gain
        elif isinstance(gain, Number):
            self.in_gains = np.full(self.in_chan, gain)
        else:
            raise TypeError("Gain needs to be either list of float.")
        
        if dur is not None and block:
            _LOGGER.info(f" Block mode recording of {dur} seconds.")
            self.rec_dur = int(self.sr * dur)
            self.rec_stream = self.pa.open(
                format=pyaudio.paFloat32,
                channels=self.out_chan,
                rate=self.sr,
                input=True,
                output=True,  
                input_device_index=self.in_idx,
                output_device_index=self.out_idx,
                frames_per_buffer=self.bs)
            # Counting here. System is blocked in the foor loop. 
            for i in range(0, int(self.sr / self.bs * dur)):
                # Apply gain here. 
                signal = decode(self.rec_stream.read(self.bs), self.in_chan)
                signal *= self.in_gains  # Apply signal gain. 
                self.record_buffer.append(signal)
            self.rec_stream.stop_stream()
            self.rec_stream.close()
            _LOGGER.info(" Record Finished.")

        elif dur is None or not block:  # non blocking mode 
            self.silence = np.zeros((self.bs, self.out_chan)) 
            callback = self._record_callback_monitor if monitor else self._record_callback
            self.rec_stream = self.pa.open(
                format=pyaudio.paFloat32,
                channels=self.out_chan,
                rate=self.sr,
                input=True,
                output=True,  
                input_device_index=self.in_idx,
                output_device_index=self.out_idx,
                frames_per_buffer=self.bs,        
                stream_callback=callback)
            self.rec_stream.start_stream()

    def _record_callback_monitor(self, in_data, frame_count, time_info, flag):
        """Callback for record stream"""
        signal = decode(in_data, self.in_chan) 
        signal *= self.in_gains  # Apply signal gain. 
        self.record_buffer.append(signal)
        # out = audio_data.astype(np.float32)  # At this stage it is finalized 
        return signal, pyaudio.paContinue   
    
    def _record_callback(self, in_data, frame_count, time_info, flag):
        """Callback for record stream"""
        signal = decode(in_data, self.in_chan) 
        signal *= self.in_gains  # Apply signal gain. 
        self.record_buffer.append(signal)
        # out = audio_data.astype(np.float32)  # At this stage it is finalized 
        return self.silence, pyaudio.paContinue
    
    def stop(self):
        try:
            
            self.rec_stream.stop_stream()
            print("stopping..")
            self.rec_stream.close()
            _LOGGER.info("record stream close. ")
        except AttributeError:
            print("Attribute error")  
            _LOGGER.info("self.rec_stream not exsist.")
            

        