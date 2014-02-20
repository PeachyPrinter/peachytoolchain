import numpy

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
    """Base class for an object that's responsible for taking left/right audio values and modulating them as needed
    to drive the printer. Also has to consider whether or not the laser is enabled, since this changes how modulation
    is performed (to signal to the printer the laser state)."""
    def __init__(self, sampling_rate):
        """
        sampling_rate -- int -- The sampling frequency of the expected audio input/output stream.
        """
        raise NotImplementedError('abstract')

    def modulate_values(self, values):
        """
        Modulates the given values according to the modulation technique used.
        Takes and returns a Nx2 numpy array of left/right +/-1.0 audio values.
        """
        raise NotImplementedError('abstract')

    @property
    def sampling_rate(self):
        """
        The current sampling rate of the audio stream.
        """
        raise NotImplementedError('abstract')

    @property
    def laser_enabled(self):
        """
        Whether or not the laser is currently enabled. Set this to change the laser state.
        """
        raise NotImplementedError('abstract')

    @property
    def waveform_period(self):
        """
        The period of the modulation waveform. The modulator ensures that looping over this period will result in a
        continuous waveform with no sudden jumps.
        """
        raise NotImplementedError('abstract')


class AmplitudeModulator(Modulator):
    """Takes a stream of stereo values and modulates their amplitude on a fixed carrier frequency. This is used with the
    hardware amplitude demodulator to allow us to send slow-moving signals over AC coupled outputs. This modulates both
    channels at the same time with the same carrier. Ideally, the carrier frequency will be a integer fraction of the
    sampling rate."""
    AM_MINIMUM_AMPLITUDE = 0.25
    AM_MAXIMUM_AMPLITUDE = 1.00
    AM_CARRIER_FREQ_LASER_ON = 8000.0
    AM_CARRIER_FREQ_LASER_OFF = AM_CARRIER_FREQ_LASER_ON/4.0
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
        # Note: Since this fixes the period to an integer number of samples, the frequency will be discretized.
        if self._laser_enabled:
            self._carrier_freq = float(self.AM_CARRIER_FREQ_LASER_ON)
        else:
            self._carrier_freq = float(self.AM_CARRIER_FREQ_LASER_OFF)
        cycle_period = int(round(float(self.NUM_CYCLES_TO_CALCULATE) * self.sampling_rate / self._carrier_freq))
        self._modulation_waveform = numpy.cos(numpy.linspace(0.0, self.NUM_CYCLES_TO_CALCULATE*2.0*numpy.pi,
                                                             num=cycle_period, endpoint=False))
        self._current_cycle = 0

    def _modulated_value_in_limits(self, modulated_values):
        return numpy.all(modulated_values < self.AM_MAXIMUM_AMPLITUDE) and numpy.all(modulated_values > self.AM_MINIMUM_AMPLITUDE)

    def modulate_values(self, values):
        num_values = values.shape[0]
        waveform_indices = numpy.remainder(numpy.arange(num_values)+self._current_cycle, self._modulation_waveform.shape[0])
        modulation_waveform = numpy.take(self._modulation_waveform, waveform_indices)
        left = values[:,0]
        right = values[:,1]
        # Shift from -/+ 1.0 to (0, 1.0)
        left = (left + 1.0) / 2.0
        right = (right + 1.0) / 2.0
        # Then shift to the min/max
        left = self.AM_MINIMUM_AMPLITUDE + left * (self.AM_MAXIMUM_AMPLITUDE-self.AM_MINIMUM_AMPLITUDE)
        right = self.AM_MINIMUM_AMPLITUDE + right * (self.AM_MAXIMUM_AMPLITUDE-self.AM_MINIMUM_AMPLITUDE)
        
        if ( not self._modulated_value_in_limits(left) or not self._modulated_value_in_limits(right)):
            raise Exception("Model exceeds bounds, try a smaller model")

        left = left * modulation_waveform
        right = right * modulation_waveform
        self._current_cycle = (self._current_cycle + num_values) % self._modulation_waveform.shape[0]
        new_values = numpy.column_stack((left, right))
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

    @property
    def waveform_period(self):
        return self._modulation_waveform.shape[0]


class DirectConnectionModulator(Modulator):
    """Takes a stream of stereo audio values and plays them mostly as-is, except that it scales them to 75% of total
    and adds a 25% amplitude side-tone for enabling the laser. Ideally, the side-tone frequency should be an integer
    fraction of the sampling rate."""
    DC_SIDE_TONE_FREQ = 11025.0
    DC_SIDE_TONE_AMPLITUDE = 0.25
    DC_AUDIO_SCALE = 0.75
    NUM_CYCLES_TO_CALCULATE = 128

    def __init__(self, sampling_rate):
        self._sampling_rate = sampling_rate
        self._laser_enabled = False
        self._side_tone_waveform = None
        self._current_cycle = None
        self._update_waveform()

    def _update_waveform(self):
        # Use a fixed set of values for modulation to speed up modulation and ensure consistency.
        # Note: Since this fixes the period to an integer number of samples, the frequency will be discretized.
        cycle_period = int(round(float(self.NUM_CYCLES_TO_CALCULATE) * self.sampling_rate / self.DC_SIDE_TONE_FREQ))
        self._side_tone_waveform = numpy.cos(numpy.linspace(0.0, self.NUM_CYCLES_TO_CALCULATE*2.0*numpy.pi,
                                                            num=cycle_period, endpoint=False))
        self._current_cycle = 0

    def modulate_values(self, values):
        num_values = values.shape[0]
        waveform_indices = numpy.remainder(numpy.arange(num_values)+self._current_cycle, self._side_tone_waveform.shape[0])
        modulation_waveform = numpy.take(self._side_tone_waveform, waveform_indices)
        left = values[:,0] * self.DC_AUDIO_SCALE
        right = values[:,1] * self.DC_AUDIO_SCALE
        if self._laser_enabled:
            left = left + modulation_waveform * self.DC_SIDE_TONE_AMPLITUDE
            right = right + modulation_waveform * self.DC_SIDE_TONE_AMPLITUDE
        self._current_cycle = (self._current_cycle + num_values) % self._side_tone_waveform.shape[0]
        new_values = numpy.column_stack((left, right))
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

    @property
    def waveform_period(self):
        return self._side_tone_waveform.shape[0]
