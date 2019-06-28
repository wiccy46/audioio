import numpy as np
import pyaudio
import logging

_LOGGER = logging.getLogger(__name__)
_LOGGER.addHandler(logging.NullHandler())

class Audioio():
    """Core class of the audioio, currently only dealing with float32, later to add more dtype in, such as int16

    Args:
      sr (int): sampling rate
      chunk (int): chunk size or buffer size
      pa (PyAudio()): pyaudio class for audio streaming


    TODO: make sure everytime a new device is set, the parameters are updated.
    """

    def __init__(self, sr=44100, chunk=256, in_device=0, out_device=1):
        self.sr = sr
        self.chunk = chunk
        self.pa = pyaudio.PyAudio()
        self._dtype = "float32"
        # Get all audio input and output
        self.il = []
        self.ol = []
        for i in range(self.pa.get_device_count()):
            if self.pa.get_device_info_by_index(i)['maxInputChannels'] > 0:
                self.il.append(self.pa.get_device_info_by_index(i))
            if self.pa.get_device_info_by_index(i)['maxOutputChannels'] > 0:
                self.ol.append(self.pa.get_device_info_by_index(i))

        self.input_gains = [1.]  # needs to be scaled based on the channels
        self.output_gains = [1.]
        self.record_buffer = []  # A buffer for long audio being recorded in.
        self.in_chan = 1  # how many channels of inputs the device has.
        self.in_idx = in_device   # TODO check default device
        self.out_idx = out_device   # same as above

    @property
    def dtype(self):
        return self._dtype

    def get_devices(self):
        """Print audio all available devices"""
        for i in range(self.pa.get_device_count()):
            print(self.pa.get_device_info_by_index(i))

    def set_device(self, in_device=0, out_device=1):
        # check how to set default devices.
        pass

    def record(self, dur=None):
        """Recording Audio

        Args:
            dur (float): if None, recording indefinitely, else, record dur seconds.

        """
        # try:
        #     # restarting recording without closing stream, resulting an unstoppable stream.
        #     # This can happen in Jupyter when you trigger record multple times without stopping it first.
        #     self.rec_stream.stop_stream()
        #     self.rec_stream.close()
        #    _LOGGER.debug("record stream close. ")
        # except AttributeError:
        #     pass

        _LOGGER.info("Start Recording")
        self.record_buffer = []  # Clear the bufferlist for new recording.
        # Input channels will be used to reshaping in_data during recording.
        self.in_chan = 1  # This needs to be done cleverly 
        self.out_chan = 2  # also need clever way 
        # self.input_channels = self.pa.get_device_info_by_index(self.input_idx).get("maxInputChannels")
        self.rec_stream = self.pa.open(
            format=pyaudio.paFloat32,
            channels=self.out_chan,
            rate=self.sr,
            input=True,
            output=True,  # Removed input_device_index. As it should listen to all.
            input_device_index=self.in_idx,
            output_device_index=self.out_idx,
            frames_per_buffer=self.chunk,
            stream_callback=self._record_callback)
        self.rec_stream.start_stream()

    def _record_callback(self, in_data, frame_count, time_info, flag):
        """Callback for record stream"""

        # The * self.ivols[0] here is problematics.
        # float32 is not 32 bit.
        audio_data = (np.frombuffer(in_data, dtype=np.float32) * self.input_gains).astype(np.float32)
        # audio_data = audio_data.reshape((len(audio_data) // self.in_chan, self.in_chan))

        # if self.emitsignal:
        #     # This part is for sending audio to pyqt for realtime plotting. Disable it for better performance.
        #     self.qt_signal.emit(audio_data)

        self.record_buffer.append(audio_data)
        return in_data, pyaudio.paContinue

    def _play_callback(self, in_data, frame_count, time_info, flag):
        """Audio callback when stream is open. This is only used for playing, not for recording.

        Args:
          in_data (bytes): audio inputs per frame/chunk
          frame_count (int): counting the frame

        Returns:
          out_data (TBD): output data per frame
          status (paStatus): paContinute or paComplete indicating whether the stream is on or not.
        """
        if (self.frameCount < self.total_chunk):
            out_data = self._outputgain(self.play_data[self.frameCount])
            self.frameCount += 1
            return out_data, pyaudio.paContinue
        else:  # The last one .
            out_data = bytes(np.zeros(self.chunk * self.output_channels))
            return out_data, pyaudio.paComplete