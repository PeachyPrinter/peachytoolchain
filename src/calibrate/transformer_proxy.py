import threading
from PySide.QtCore import QObject, Signal, Slot

class PositionToAudioTransformerProxy(QObject):
    """
    Provides a generator-like object for the AudioServer, allowing requests for audio samples to be proxied
    as requests for position samples, which are then transformed through the PositionToAudioTransformer.
    """
    clippingStateChanged = Signal(bool)
    CLIPPING_HOLD_NUM_SAMPLES = 1024 # If clipping occurs, wait this many samples before resetting clip state

    def __init__(self, transformer, generator):
        QObject.__init__(self)
        self._generator = generator
        self.transformer = transformer
        self._clip_hold_count = 0 # Number of samples since clipping was last detected
        self._clip_state = False  # True if clipping has occurred within the last CLIPPING_HOLD_NUM_SAMPLES samples
        self._lock = threading.Lock()

    def nextN(self, N):
        with self._lock:
            points = self._generator.nextN(N)
            samples = self.transformer.transform_points(points)
            samples = self._clip_samples(samples)
            return samples

    @property
    def clipState(self):
        with self._lock:
            return self._clip_state

    @property
    def generator(self):
        with self._lock:
            return self._generator

    @generator.setter
    def generator(self, generator):
        with self._lock:
            self._generator = generator

    def _clip_samples(self, samples):
        new_samples = []
        for (left, right) in samples:
            if left < -1.0 or left > 1.0 or right < -1.0 or right > 1.0:
                self._clip_hold_count = 0
                if self._clip_state == False:
                    self._clip_state = True
                    self.clippingStateChanged.emit(True)
                left = min(1.0, max(-1.0, left))
                right = min(1.0, max(-1.0, right))
            elif self._clip_state == True:
                if self._clip_hold_count > self.CLIPPING_HOLD_NUM_SAMPLES:
                    self._clip_state = False
                    self.clippingStateChanged.emit(False)
                else:
                    self._clip_hold_count += 1
            new_samples.append((left, right))
        return new_samples

