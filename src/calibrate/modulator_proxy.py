from PySide.QtCore import QObject
import threading

class ModulatorProxy(QObject):
    """Provides a generator-like interface for the AudioServer. allowing requests for audio values to be proxied through
    a modulator."""
    def __init__(self, modulator, generator):
        QObject.__init__(self)
        self._modulator = modulator
        self._generator = generator
        self._lock = threading.Lock()

    def nextN(self, n):
        with self._lock:
            values = self.generator.nextN(n)
            values = self.modulator.modulate_values(values)
        return values

    @property
    def modulator(self):
        return self._modulator

    @modulator.setter
    def modulator(self, modulator):
        with self._lock:
            self._modulator = modulator

    @property
    def generator(self):
        return self._generator
    @generator.setter
    def generator(self, generator):
        with self._lock:
            self._generator = generator

    @property
    def laser_enabled(self):
        return self._modulator.laser_enabled
    @laser_enabled.setter
    def laser_enabled(self, enabled):
        with self._lock:
            self._modulator.laser_enabled = enabled
