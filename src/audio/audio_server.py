import pyaudio
import threading
from . import util as audio_util
import time

class AudioServer(threading.Thread):
    def __init__(self, generator, sampling_rate):
        """
        generator -- provides samples to be played -- must have 'nextN'
        sampling_rate -- int -- The number of samples per second for playback
        """
        threading.Thread.__init__(self)
        self.running = False
        self.sampling_rate = sampling_rate
        self.generator = generator

    def run(self):
        self.running = True
        self.pa = pyaudio.PyAudio()
        self.stream = self.pa.open(format=self.pa.get_format_from_width(2, unsigned=False),
                 channels=2,
                 rate=self.sampling_rate,
                 output=True,
                 frames_per_buffer=int(self.sampling_rate/8))
        while self.running:
            num_next = self.stream.get_write_available()
            if num_next > int(self.sampling_rate/16):
                values = self.generator.nextN(num_next)
                frames = audio_util.convert_values_to_frames(values)
                self.stream.write(frames)
            else:
                time.sleep(0.01)
        self.stream.stop_stream()
        self.stream.close()
        self.pa.terminate()

    def stop(self):
        self.running = False
        self.join(10.0)
        if self.is_alive():
            print('WARNING: AudioServer did not stop after 10 seconds')
