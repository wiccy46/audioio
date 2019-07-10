# console.py
import logging
import time
import pyaudio
import numpy as np 
from . import BasicAudioio


_LOGGER = logging.getLogger(__name__)
_LOGGER.addHandler(logging.NullHandler())


class Audioio(BasicAudioio):
    def __init__(self, sr=44100, bs=1024, in_device=0, out_device=1):
        super(Audioio, self).__init__(sr=sr, bs=bs, in_device=in_device, out_device=out_device)

    def record(self, gain=[1.], block=False, dur=None):
        """Recording Audio

        Args:
            dur (float): if None, recording indefinitely, else, record dur seconds.
            block (bool): block mode 
        """
        try:
            # restarting recording without closing stream, resulting an unstoppable stream.
            # This can happen in Jupyter when you trigger record multple times without stopping it first.
            self.rec_stream.stop_stream()
            self.rec_stream.close()
            _LOGGER.info("record stream close. ")
        except AttributeError:
            pass

        _LOGGER.info("Start Recording")
        self.record_buffer = []  # Clear the bufferlist for new recording.
        # self.input_channels = self.pa.get_device_info_by_index(self.input_idx).get("maxInputChannels")
        self.in_gains = gain

        if dur is not None and block:
            # blocking recording 
            self.rec_dur = int(self.sr * dur)
            _LOGGER.info("fix duration start.")
            rec_stream = self.pa.open(
                format=pyaudio.paFloat32,
                channels=self.out_chan,
                rate=self.sr,
                input=True,
                output=True,  # Removed input_device_index. As it should listen to all.
                input_device_index=self.in_idx,
                output_device_index=self.out_idx,
                frames_per_buffer=self.bs)
            
            for i in range(0, int(self.sr / self.bs * dur)):
                self.record_buffer.append(np.frombuffer(rec_stream.read(self.bs), dtype=np.float32))
            rec_stream.stop_stream()
            rec_stream.close()
            _LOGGER.info("fix duration stop.")

        else:
            # non blocking mode 
            self.rec_stream = self.pa.open(
                format=pyaudio.paFloat32,
                channels=self.out_chan,
                rate=self.sr,
                input=True,
                output=True,  # Removed input_device_index. As it should listen to all.
                input_device_index=self.in_idx,
                output_device_index=self.out_idx,
                frames_per_buffer=self.bs,
                stream_callback=self._record_callback)
            self.rec_stream.start_stream()

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
        