import threading
import pyaudio
import math
import struct
import time

class DripDetector(threading.Thread):
    MONO_WAVE_STRUCT_FMT = "h"
    MONO_WAVE_STRUCT = struct.Struct(MONO_WAVE_STRUCT_FMT)
    MAX_S16 = math.pow(2, 15)-1
    def __init__(self, drips_per_mm, initial_height = 0.0, sampling_frequency = 48000, threshold = 400, release_ms = 6, echo_drips = False):
        threading.Thread.__init__(self)
        self._drips_per_mm = drips_per_mm * 1.0
        self._sampling_frequency = sampling_frequency
        self._threshold = self.MAX_S16 - threshold
        self._release = self._sampling_frequency / 1000 * release_ms
        self._echo_drips = echo_drips
        self._running = False
        self._num_drips = 0
        self._drips_per_mm = 1.0
        self._hold_samples = 0
        self._indrip = False
        self.instream = None

        self.set_drips_per_mm(drips_per_mm)

    def set_drips_per_mm(self,number_drips_per_mm):
        self._drips_per_mm = number_drips_per_mm

    def get_height_mm(self):
        if (self._num_drips == 0):
            return 0.0
        return (self._num_drips * 1.0) / self._drips_per_mm

    def run(self):
        pa = pyaudio.PyAudio()
        self.instream = pa.open(
                format=pa.get_format_from_width(2, unsigned=False),
                 channels=1,
                 rate=self._sampling_frequency,
                 input=True,
                 frames_per_buffer=int(self._sampling_frequency/8)
                 )
        self.instream.start_stream()
        self._running = True
        while(self._running):
            buffer_frames_available = self.instream.get_read_available()
            if buffer_frames_available:
                frames = self.instream.read(buffer_frames_available)
                self._add_frames(frames)

    def stop(self):
        self._running = False
        if self.instream:
            self.instream.stop_stream()
            time.sleep(0.1) # Waiting for current op to compelete
            self.instream.close()
        self.join(10.0)
        if self.is_alive():
            print('WARNING: DripDetector failed to stop')

    def _add_frames(self, frames):
        hold_samples_c = 250

        for offset in range(0, len(frames), self.MONO_WAVE_STRUCT.size):
            value = self.MONO_WAVE_STRUCT.unpack_from(frames, offset)[0]
            if (value >=  self._threshold):
                self._indrip = True
                self._hold_samples = self._release
            else:
                if (self._hold_samples > 0):
                    self._hold_samples -= 1
                else:
                    if (self._indrip == True ):
                        self._num_drips += 1
                        if (self._echo_drips):
                            print("Drips: %d" % self._num_drips)
                        self._indrip = False
                        self._hold_samples = self._release



