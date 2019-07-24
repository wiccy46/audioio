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
        super(Audioio, self).__init__(sr=sr, bs=bs, device=[None, None])

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
            pass
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
            rec_stream = self.pa.open(
                format=pyaudio.paFloat32,
                channels=self.out_chan,
                rate=self.sr,
                input=True,
                output=True,  # Removed input_device_index. As it should listen to all.
                input_device_index=self.in_idx,
                output_device_index=self.out_idx,
                frames_per_buffer=self.bs)
            # Counting here. System is blocked in the foor loop. 
            for i in range(0, int(self.sr / self.bs * dur)):
                # Apply gain here. 
                signal = decode(rec_stream.read(self.bs), self.in_chan)
                signal *= self.in_gains  # Apply signal gain. 
                self.record_buffer.append(signal)
            rec_stream.stop_stream()
            rec_stream.close()
            _LOGGER.info(" Record Finished.")

        # else:
        #     # non blocking mode 
        #     self.rec_stream = self.pa.open(
        #         format=pyaudio.paFloat32,
        #         channels=self.out_chan,
        #         rate=self.sr,
        #         input=True,
        #         output=True,  # Removed input_device_index. As it should listen to all.
        #         input_device_index=self.in_idx,
        #         output_device_index=self.out_idx,
        #         frames_per_buffer=self.bs,        
        #         stream_callback=self._record_callback)
        #     self.rec_stream.start_stream()

    def _record_callback(self, in_data, frame_count, time_info, flag):
        """Callback for record stream"""
        audio_data = np.frombuffer(in_data, dtype=np.float32) * self.in_gains  # convert bytes to float. 
        # Next work with shapes if the data is in higher dimension. 
        
        # self.test_time.append(time_info['output_buffer_dac_time'] - time_info['input_buffer_adc_time'])
        # """This is probably not an efficient way. Try to use limiter or compressor instead"""

        audio_data = self.processing(audio_data)

        # # audio_data = audio_data.reshape((len(audio_data) // self.in_chan, self.in_chan))

        out = audio_data.astype(np.float32)  # At this stage it is finalized 
        self.record_buffer.append(out)  # Record data
        return out, pyaudio.paContinue

    def processing(self, x):
        return x  # Currently it is not doing anything. 
        