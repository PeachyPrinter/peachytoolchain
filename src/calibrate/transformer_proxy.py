import threading
from PySide.QtCore import QObject

class PositionToAudioTransformerProxy(QObject):
    """
    Provides a generator-like object for the AudioServer, allowing requests for audio samples to be proxied
    as requests for position samples, which are then transformed through the PositionToAudioTransformer.
    """
    def __init__(self, transformer, generator):
        QObject.__init__(self)
        self._generator = generator
        self.transformer = transformer
        self._lock = threading.Lock()

    def nextN(self, N):
        with self._lock:
            points = self._generator.nextN(N)
            samples = self.transformer.transform_points(points)
            return samples

    @property
    def generator(self):
        with self._lock:
            return self._generator

    @generator.setter
    def generator(self, generator):
        with self._lock:
            self._generator = generator
