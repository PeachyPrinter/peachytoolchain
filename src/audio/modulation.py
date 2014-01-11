import math

class ModulationTypes:
    DC = 'dc'
    AM = 'am'


def getModulator(modulation_type, sampling_rate):
    if modulation_type == ModulationTypes.DC:
        return DirectConnectionModulator(sampling_rate)
    elif modulation_type == ModulationTypes.AM:
        return AmplitudeModulator(sampling_rate)
    else:
        raise NotImplementedError('No modulator class defined for modulation type "%s".' % (modulation_type,))


class Modulator(object):
    def __init__(self, sampling_rate):
        raise NotImplementedError('abstract')

    def modulate_values(self, values):
        raise NotImplementedError('abstract')

    @property
    def sampling_rate(self):
        raise NotImplementedError('abstract')

    @property
    def laser_enabled(self):
        raise NotImplementedError('abstract')


class AmplitudeModulator(Modulator):
    """Takes a stream of stereo values and modulates their amplitude on a fixed carrier frequency. This is used with the
    hardware amplitude demodulator to allow us to send slow-moving signals over AC coupled outputs. This modulates both
    channels at the same time with the same carrier. Ideally, the carrier frequency will be a integer fraction of the
    sampling rate."""
    AM_MINIMUM_AMPLITUDE = 0.25
    AM_MAXIMUM_AMPLITUDE = 1.00
    AM_CARRIER_FREQ_LASER_ON = 11025.0
    AM_CARRIER_FREQ_LASER_OFF = 11025.0/4.0 # 11025/4
    NUM_CYCLES_TO_CALCULATE = 128 # The calculated modulation waveform will contain this many full cycles before repeating

    def __init__(self, sampling_rate):
        self._sampling_rate = float(sampling_rate)
        self._laser_enabled = False
        self._carrier_freq = None
        self._modulation_waveform = None
        self._current_cycle = None
        self._update_modulation()

    def _update_modulation(self):
        # Use a fixed set of values for modulation to speed up modulation and ensure consistency.
        if self._laser_enabled:
            self._carrier_freq = float(self.AM_CARRIER_FREQ_LASER_ON)
        else:
            self._carrier_freq = float(self.AM_CARRIER_FREQ_LASER_OFF)
        cycle_period = int(round(float(self.NUM_CYCLES_TO_CALCULATE) * self.sampling_rate / self._carrier_freq))
        self._modulation_waveform = [math.cos(2.0*math.pi*(
                float(cycle) * float(self._carrier_freq) / float(self._sampling_rate)
            )) for cycle in range(cycle_period)]
        self._current_cycle = 0

    def modulate_values(self, values):
        new_values = []
        for (left, right) in values:
            # Shift from -/+ 1.0 to (0, 1.0)
            left = (left + 1.0) / 2.0
            right = (right + 1.0) / 2.0
            # Then shift to the min/max
            left = self.AM_MINIMUM_AMPLITUDE + left * (self.AM_MAXIMUM_AMPLITUDE-self.AM_MINIMUM_AMPLITUDE)
            right = self.AM_MINIMUM_AMPLITUDE + right * (self.AM_MAXIMUM_AMPLITUDE-self.AM_MINIMUM_AMPLITUDE)
            left *= self._modulation_waveform[self._current_cycle]
            right *= self._modulation_waveform[self._current_cycle]
            new_values.append((left, right))
            self._current_cycle = (self._current_cycle + 1) % len(self._modulation_waveform)
        return new_values

    @property
    def sampling_rate(self):
        return self._sampling_rate
    @sampling_rate.setter
    def sampling_rate(self, rate):
        self._sampling_rate = rate
        self._update_modulation()

    @property
    def laser_enabled(self):
        return self._laser_enabled
    @laser_enabled.setter
    def laser_enabled(self, enabled):
        self._laser_enabled = enabled
        self._update_modulation()


class DirectConnectionModulator(Modulator):
    """Takes a stream of stereo audio values and plays them mostly as-is, except that it scales them to 75% of total
    and adds a 25% amplitude side-tone for enabling the laser. Ideally, the side-tone frequency should be an integer
    fraction of the sampling rate."""
    DC_SIDE_TONE_FREQ = 11025.0
    DC_SIDE_TONE_AMPLITUDE = 0.25
    DC_AUDIO_SCALE = 0.75

    def __init__(self, sampling_rate):
        self._sampling_rate = sampling_rate
        self._laser_enabled = False
        self._side_tone_waveform = None
        self._current_cycle = None
        self._update_waveform()

    def _update_waveform(self):
        # Use a fixed set of values for the waveform to speed up modulation and ensure consistency.
        cycle_period = int(round(self.sampling_rate / self.DC_SIDE_TONE_FREQ))
        self._side_tone_waveform = [math.cos(2.0*math.pi*(
                float(cycle) * float(self.DC_SIDE_TONE_FREQ) / float(self._sampling_rate)
            )) for cycle in range(cycle_period)]

        self._current_cycle = 0

    def modulate_values(self, values):
        new_values = []
        for (left, right) in values:
            left *= self.DC_AUDIO_SCALE
            right *= self.DC_AUDIO_SCALE
            if self._laser_enabled:
                left += self.DC_SIDE_TONE_AMPLITUDE*self._side_tone_waveform[self._current_cycle]
                right += self.DC_SIDE_TONE_AMPLITUDE*self._side_tone_waveform[self._current_cycle]
            new_values.append((left, right))
            self._current_cycle = (self._current_cycle + 1) % len(self._side_tone_waveform)
        return new_values

    @property
    def sampling_rate(self):
        return self._sampling_rate
    @sampling_rate.setter
    def sampling_rate(self, rate):
        self._sampling_rate = rate
        self._update_waveform()

    @property
    def laser_enabled(self):
        return self._laser_enabled
    @laser_enabled.setter
    def laser_enabled(self, enabled):
        self._laser_enabled = enabled