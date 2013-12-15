import math

class AmplitudeModulator(object):
    """Takes a stream of stereo values and modulates their amplitude on a fixed carrier frequency. This is used with the
    hardware amplitude demodulator to allow us to send slow-moving signals over AC coupled outputs. This modulates both
    channels at the same time with the same carrier. Ideally, the carrier frequency will be a integer fraction of the
    sampling rate."""
    def __init__(self, sampling_rate, carrier_freq):
        self._sampling_rate = sampling_rate
        self._carrier_freq = carrier_freq
        self._modulation_waveform = None
        self._current_cycle = None
        self._update_modulation()

    def _update_modulation(self):
        # Use a fixed set of values for modulation to speed up modulation and ensure consistency.
        cycle_period = int(round(self.sampling_rate / self.carrier_freq))
        self._modulation_waveform = [math.cos(2.0*math.pi*(float(cycle) / float(cycle_period))) for cycle in range(cycle_period)]
        self._current_cycle = 0

    def modulate_values(self, values):
        new_values = []
        for (left, right) in values:
            old_l, old_r = left, right
            left *= self._modulation_waveform[self._current_cycle]
            right *= self._modulation_waveform[self._current_cycle]
            new_values.append((left, right))
            self._current_cycle = (self._current_cycle + 1) % len(self._modulation_waveform)
            #print('(%f, %f) -> (%f, %f)' % (old_l, old_r, left, right))
        return new_values

    @property
    def sampling_rate(self):
        return self._sampling_rate
    @sampling_rate.setter
    def sampling_rate(self, rate):
        self._sampling_rate = rate
        self._update_modulation()

    @property
    def carrier_freq(self):
        return self._carrier_freq
    @carrier_freq.setter
    def carrier_freq(self, freq):
        self._carrier_freq = freq
        self._update_modulation()
