#!/usr/bin/python3.2
import sys
from PySide import QtGui
from calibrate.mainwindow import MainWindow
from audio.tuning_parameters import TuningParameters
from audio.audio_server import AudioServer
from audio.transform import AudioTransformer
from calibrate import waveform_generators

app = QtGui.QApplication(sys.argv)
widget = QtGui.QMainWindow()
generator = waveform_generators.NullGenerator()
tuning = TuningParameters()
transformer = AudioTransformer(tuning)
audio = AudioServer(generator, transformer)
generators = {'Square': waveform_generators.SquareGenerator,
              'Star': waveform_generators.StarGenerator}
ui = MainWindow(tuning, audio, generators)
ui.setupUi(widget)
widget.show()
print('start audio')
audio.start()
retcode = app.exec_()
print('stop audio')
audio.stop()
sys.exit(retcode)
