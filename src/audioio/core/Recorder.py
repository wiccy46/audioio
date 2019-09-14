import logging
from numbers import Number
import numpy as np
import pyaudio
from .Core import Aiocore
from .utils import encode, decode

_LOGGER = logging.getLogger(__name__)
_LOGGER.addHandler(logging.NullHandler())


class Recorder(Aiocore):
    def __init__(self, sr=44100, bs=1024, device_indices=(None, None)):
        super().__init__()
        self.record_buffer = []

    def clear_record_buffer(self):
        self.record_buffer = []  #TODO Consider using a fixed length for performance.
        
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
            If float, apply the gain on all channel,
            if list apply to individual channel accordingly.
        dur : float or None
            Default is None, the recording is switched on definitely.
            If number, record a fixed duration in seconds
        block : bool
            Decide whether record block the process or not.
        monitor : bool
            Only available in non-blocking mode,
            allow directly monitoring as gained input will be sent to outputs. Be vary of the feedback.
        """
        try:
            # Always check if there is an unclosed stream
            self.record_stream.stop_stream()
            self.record_stream.close()
            _LOGGER.info("record stream close. ")
        except AttributeError:
            _LOGGER.info("self.record_stream not exsist.")
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
            self.record_stream = self.pa.open(
                format=pyaudio.paFloat32,
                channels=self.input_channels,
                rate=self.sr,
                input=True,
                output=True,
                input_device_index=self.input_index,
                output_device_index=self.output_index,
                frames_per_buffer=self.bs,
                stream_callback=callback)
            self.record_stream.start_stream()

    def _record_callback_monitor(self, in_data, frame_count, time_info, flag):
        """Callback for record stream"""
        signal = decode(in_data, self.input_channels)
        signal *= self.input_gains
        #process 0- > find pitch
        self.record_buffer.append(signal)
        # out = audio_data.astype(np.float32)  # At this stage it is finalized
        return signal, pyaudio.paContinue
    
    def _record_callback(self, in_data, frame_count, time_info, flag):
        """Callback for record stream"""
        signal = decode(in_data, self.input_channels)
        signal *= self.input_gains  # Apply signal gain.
        self.record_buffer.append(signal)
        return self.silence, pyaudio.paContinue

    def _block_mode_recording(self, dur):
        _LOGGER.info(f" Block mode recording of {dur} seconds.")
        self.record_duration = int(self.sr * dur)
        print("Input channel: ", self.input_channels)
        self.record_stream = self.pa.open(
            format=pyaudio.paFloat32,
            channels=self.input_channels,
            rate=self.sr,
            input=True,
            output=True,
            input_device_index=self.input_index,
            output_device_index=self.output_index,
            frames_per_buffer=self.bs)
        # Counting here. System is blocked in the foor loop.
        for i in range(0, int(self.sr / self.bs * dur)):
            # Apply gain here.
            signal = decode(self.record_stream.read(self.bs), self.input_channels)
            signal *= self.input_gains  # Apply signal gain.
            self.record_buffer.append(signal)
        self.record_stream.stop_stream()
        self.record_stream.close()
        _LOGGER.info(" Record Finished.")


    def stop(self):
        """Stop recording"""
        try:
            self.record_stream.stop_stream()
            self.record_stream.close()
            _LOGGER.info("record stream close. ")
        except AttributeError:
            print("Attribute error")
            _LOGGER.info("self.record_stream not exsist.")
