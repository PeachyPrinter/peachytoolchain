from PySide.QtCore import QObject

class ModulatorProxy(QObject):
    """Provides a generator-like interface for the AudioServer. allowing requests for audio values to be proxied through
    a modulator."""
    def __init__(self, modulator, generator):
        QObject.__init__(self)
        self.modulator = modulator
        self.generator = generator

    def nextN(self, n):
        values = self.generator.nextN(n)
        values = self.modulator.modulate_values(values)
        return values
