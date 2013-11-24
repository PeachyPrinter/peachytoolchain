import pyaudio
import threading
from . import util as audio_util
import time

WAVE_RATE = 8000

class AudioServer(threading.Thread):
    def __init__(self, generator, transformer):
        threading.Thread.__init__(self)
        self.running = False
        self.set_generator(generator)
        self._transformer = transformer

    def run(self):
        self.running = True
        self.pa = pyaudio.PyAudio()
        self.stream = self.pa.open(format=self.pa.get_format_from_width(2, unsigned=False),
                 channels=2,
                 rate=WAVE_RATE,
                 output=True,
                 frames_per_buffer=int(WAVE_RATE/8))
        while self.running:
            num_next = self.stream.get_write_available()
            if num_next > int(WAVE_RATE/16):
                values = self.generator.nextN(num_next)
                values = self._transformer.transform_values(values)
                frames = audio_util.convert_values_to_frames(values)
                self.stream.write(frames)
            else:
                time.sleep(0.01)
        print('stopping')
        self.stream.stop_stream()
        self.stream.close()
        self.pa.terminate()

    def stop(self):
        self.running = False
        self.join(10.0)
        if self.is_alive():
            print('WARNING: AudioServer did not stop after 10 seconds')

    def set_generator(self, generator):
        generator.set_wave_rate(WAVE_RATE)
        self.generator = generator

    def get_generator(self):
        return self._generator


