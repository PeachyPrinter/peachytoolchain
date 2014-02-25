import threading
import pyaudio
import math
import struct

class DripDetector(threading.Thread):
    INPUT_WAVE_RATE = 8000
    FILTER_ON_TIME = 0.05
    FILTER_OFF_TIME = 0.05
    MONO_WAVE_STRUCT_FMT = "h"
    MONO_WAVE_STRUCT = struct.Struct(MONO_WAVE_STRUCT_FMT)
    MAX_S16 = math.pow(2, 15)-1

    _running = False
    _num_drips = 0
    _drips_per_mm = 1
    _current_time = 0.0
    _time_step = 1.0/INPUT_WAVE_RATE
    _indrip = False
    _hold_time = 0.0

    def __init__(self, drips_per_mm, initial_height = 0.0):
        threading.Thread.__init__(self)
        self.set_drips_per_mm(drips_per_mm)

    def set_drips_per_mm(self,number_drips_per_mm):
        self._drips_per_mm = number_drips_per_mm

    def get_height_mm(self):
        if (self._num_drips == 0):
            return 0
        return self._num_drips / self._drips_per_mm

    def run(self):
        pa = pyaudio.PyAudio()
        self.instream = pa.open(
                format=pa.get_format_from_width(2, unsigned=False),
                 channels=1,
                 rate=self.INPUT_WAVE_RATE,
                 input=True,
                 frames_per_buffer=int(self.INPUT_WAVE_RATE/8)
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
        self.instream.stop_stream()
        self.instream.close()
        self.join(10.0)
        if self.is_alive():
            print('WARNING: DripDetector failed to stop')

    _hold_samples = 0
    def _add_frames(self, frames):
        threshold = self.MAX_S16 - 2000
        hold_samples_c = 1000

        for offset in range(0, len(frames), self.MONO_WAVE_STRUCT.size):
            value = self.MONO_WAVE_STRUCT.unpack_from(frames, offset)[0]
            # self._current_time += self._time_step
            if (self._hold_samples > 0):
                self._hold_samples -= 1
            else:
                if (value >= threshold):
                   self._indrip = True
                   self._hold_samples = hold_samples_c
                else:
                    if (self._indrip == True ):
                        self._num_drips += 1
                        self._indrip = False
                        self._hold_samples = hold_samples_c
                
            # self._num_drips += 1

            # if self._indrip:
            #     if value < self.MAX_S16/8.0:
            #         self._hold_time += self._time_step
            #         if self._hold_time >= self.FILTER_OFF_TIME:
            #             # End of drip
            #             self._indrip = False
            #             self._hold_time = 0.0
            #     else:
            #         # Another high in the middle of the on state
            #         self.hold_time = 0.0
            # else:
            #     if value >= self.MAX_S16/8.0:
            #         self._hold_time += self._time_step
            #         if self._hold_time >= self.FILTER_ON_TIME:
            #             # Drip confirmed
            #             self._indrip = True
            #             self._hold_time = 0.0
            #             self._num_drips += 1
            #     else:
            #         # Another low while waiting for a drip
            #         self._hold_time = 0.0

class CureRateCalibrator(object):

    def __init__(self,drip_detector,drips_per_mm):
        if(drips_per_mm <= 0.0):
            raise Exception("drips_per_mm must be a positive number greater then 0 was: %s" % drips_per_mm)
        self._drip_detector = drip_detector
        self._drips_per_mm = drips_per_mm

    def current_height_mm(self):
        return self._drip_detector.num_drips / self._drips_per_mm

    def start(self):
        #write a base 2mm
        #
        #print solid for 1 mm and record max sublayers
        #print next 1mm skipping every 10th sublayer
        #print next 1mm skipping every 9th sublayer
        #print next 1mm skipping every 8th sublayers...


        pass
