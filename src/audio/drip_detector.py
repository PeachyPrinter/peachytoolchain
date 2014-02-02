import math
from collections import deque
from audio.util import MONO_WAVE_STRUCT, MAX_S16

class DripDetector(object):
    FILTER_ON_TIME = 0.01 # Seconds
    FILTER_OFF_TIME = 0.02 # Seconds

    def __init__(self, wave_rate, debug=False):
        self.wave_rate = wave_rate
        self.debug = debug
        self.state = False # False is out of drip, True is in drip
        self.hold_time = 0.0 # Start off with no history of trying to change state
        self._current_time = 0.0
        self._time_step = 1.0/self.wave_rate
        self.num_drips = 0
        if self.debug:
            self.drip_times = deque([], 10)
            self._last_drip_time = 0.0

    def add_frames(self, frames):
        for offset in range(0, len(frames), MONO_WAVE_STRUCT.size):
            value = MONO_WAVE_STRUCT.unpack_from(frames, offset)[0]
            self._current_time += self._time_step
            if self.state:
                # In drip -- test off time
                if value < MAX_S16/8.0:
                    self.hold_time += self._time_step
                    if self.hold_time >= self.FILTER_OFF_TIME:
                        # End of drip
                        self.state = False
                        self.hold_time = 0.0
                else:
                    # Another high in the middle of the on state
                    self.hold_time = 0.0
            else:
                # Out of drip -- test on time
                if value >= MAX_S16/8.0:
                    self.hold_time += self._time_step
                    if self.hold_time >= self.FILTER_ON_TIME:
                        # Drip confirmed
                        self.state = True
                        self.hold_time = 0.0
                        self.num_drips += 1
                        if self.debug:
                            self.drip_times.append(self._current_time-self._last_drip_time)
                            self._last_drip_time = self._current_time
                            drip_rate = self._calculate_drip_rate()
                            print('Drip detected num=%d, rate=%s' % (self.num_drips, drip_rate))
                else:
                    # Another low while waiting for a drip
                    self.hold_time = 0.0

    def _calculate_drip_rate(self):
        if len(self.drip_times) < 5:
            return 'N/A'
        avg_time = sum(self.drip_times) / len(self.drip_times)
        avg_rate = 1.0/avg_time
        return '%2.2f dps' % avg_rate


class VirtualDripDetector(object):
    """Like the real drip detector, but ignores the values given to it and instead
    counts drips at a fixed rate. Use for testing purposes."""
    def __init__(self, sampling_rate, drip_rate):
        print('*** Using virtual drip detector with rate=%f drips/second.' % drip_rate)
        self._sampling_rate = sampling_rate
        self._drip_rate = drip_rate
        self._drip_per_frame = float(drip_rate) / float(self._sampling_rate)
        self._drip_remainder = 0.0
        self.num_drips = 0

    def add_frames(self, frames):
        num_frames = len(frames) / MONO_WAVE_STRUCT.size
        self._drip_remainder += num_frames * self._drip_per_frame
        num_drips = int(math.floor(self._drip_remainder))
        self.num_drips += num_drips
        self._drip_remainder -= float(num_drips)
        if num_drips:
            print('*** Virtual drip: num_drips=%d, drip_remainder=%f' % (self.num_drips, self._drip_remainder))
