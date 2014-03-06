#!/usr/bin/env python3
from PySide import QtGui
import sys
import traceback
import os

from audio.audio_server import AudioServer
from audio.transform import PositionToAudioTransformer
from audio.tuning_parameters import TuningParameters, TuningParameterCollection
from audio.modulation import ModulationTypes, getModulator
from calibrate import shape_generators
from calibrate.mainwindow import MainWindow
from calibrate.plane_2d_to_3d_adapter import Plane2dTo3dAdapter
from calibrate.transformer_proxy import PositionToAudioTransformerProxy
from calibrate.modulator_proxy import ModulatorProxy

os.environ['LOG_LEVEL'] = 'warning'
SAMPLING_RATE = 44100

app = QtGui.QApplication(sys.argv)
widget = QtGui.QMainWindow()
generator = shape_generators.NullGenerator(SAMPLING_RATE, 1.0, 1.0, (0.0, 0.0))
height_adapter = Plane2dTo3dAdapter(generator, 0.0)
tuning = TuningParameterCollection()
transformer = PositionToAudioTransformer(tuning)
transformer_proxy = PositionToAudioTransformerProxy(transformer, height_adapter)
modulator = getModulator(ModulationTypes.AM, SAMPLING_RATE)
modulator.laser_enabled = True
modulator_proxy = ModulatorProxy(modulator, transformer_proxy)
audio = AudioServer(modulator_proxy, SAMPLING_RATE)
audio.start()

generators = {'Square': shape_generators.SquareGenerator,
              'Star': shape_generators.StarGenerator,
              '0 : None': shape_generators.NullGenerator,
              'Yline': shape_generators.YlineGenerator,
              'Xline': shape_generators.XlineGenerator,
              'Grid': shape_generators.GridGenerator,
              'File': shape_generators.ObjFileGenerator
              }
retcode = 777
try:
    mainwindow = MainWindow(tuning, modulator_proxy, generators, height_adapter, SAMPLING_RATE)
    mainwindow.show()
    retcode = app.exec_()
except Exception as ex:
    print(ex.message)
    traceback.print_exc()
    retcode = 888
    raise ex 
finally:
    audio.stop()
    sys.exit(retcode)
