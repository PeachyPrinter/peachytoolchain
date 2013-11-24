from PySide import QtCore, QtGui
import os
import os.path

from .ui_mainwindow import Ui_MainWindow
from audio.tuning_parameter_file import TuningParameterFileHandler

class MainWindow(Ui_MainWindow):
    def __init__(self, tuning_parameters, audio_server, generators):
        self.tuning_parameters = tuning_parameters
        self.audio_server = audio_server
        self.generators = generators
        self.generator = None

    def setupUi(self, MainWindow):
        Ui_MainWindow.setupUi(self, MainWindow)
        self.setup_signals()
        self.setup_models()
        self.setup_initial_values()

    def setup_signals(self):
        self.x_offset_spin.valueChanged.connect(self.x_offset_changed)
        self.y_offset_spin.valueChanged.connect(self.y_offset_changed)
        self.x_scale_spin.valueChanged.connect(self.x_scale_changed)
        self.y_scale_spin.valueChanged.connect(self.y_scale_changed)
        self.rotation_spin.valueChanged.connect(self.rotation_changed)
        self.x_shear_spin.valueChanged.connect(self.x_shear_changed)
        self.y_shear_spin.valueChanged.connect(self.y_shear_changed)
        self.pattern_combobox.currentIndexChanged.connect(self.pattern_changed)
        self.speed_spin.valueChanged.connect(self.speed_changed)
        self.save_button.clicked.connect(self.save_clicked)
        self.load_button.clicked.connect(self.load_clicked)

    def x_offset_changed(self, value):
        self.tuning_parameters.x_offset = value

    def y_offset_changed(self, value):
        self.tuning_parameters.y_offset = value

    def x_scale_changed(self, value):
        self.tuning_parameters.x_scale = value

    def y_scale_changed(self, value):
        self.tuning_parameters.y_scale = value

    def rotation_changed(self, value):
        self.tuning_parameters.rotation = value

    def x_shear_changed(self, value):
        self.tuning_parameters.x_shear = value

    def y_shear_changed(self, value):
        self.tuning_parameters.y_shear = value

    def setup_models(self):
        self.generator_list_model = QtGui.QStringListModel()
        self.generator_list_model.setStringList(sorted(self.generators.keys()))

    def setup_initial_values(self):
        self.pattern_combobox.setModel(self.generator_list_model)
        self.pattern_combobox.setCurrentIndex(0)

    def pattern_changed(self, index):
        pattern_name = self.generator_list_model.data(
            self.generator_list_model.index(index),
            QtCore.Qt.DisplayRole
        )
        self.generator = self.generators[pattern_name]()
        self.generator.set_speed(self.speed_spin.value())
        self.audio_server.set_generator(self.generator)

    def speed_changed(self, speed):
        self.generator.set_speed(speed)

    def save_clicked(self):
        (filename, selected_filter) = QtGui.QFileDialog.getSaveFileName(
            self.centralwidget, #parent
            "Save tuning parameters", #caption
        )
        if not filename:
            return
        TuningParameterFileHandler.write_to_file(self.tuning_parameters, filename)

    def load_clicked(self):
        (filename, selected_filter) = QtGui.QFileDialog.getOpenFileName(
            self.centralwidget, #parent
            "Open tuning parameter file", #caption
        )
        if not filename:
            return
        if not os.path.exists(filename):
            QtGui.QMessageBox.critical(
                parent=self,
                caption="No such file",
                text="Unable to open file %s: no such file exists." % filename,
            )
            return
        tuning_parameters = TuningParameterFileHandler.read_from_file(filename)
        self.tuning_parameters.update(tuning_parameters)
        self._update_tuning_parameters()

    def _update_tuning_parameters(self):
        tp = self.tuning_parameters
        self.x_offset_spin.setValue(tp.x_offset)
        self.y_offset_spin.setValue(tp.y_offset)
        self.rotation_spin.setValue(tp.rotation)
        self.x_shear_spin.setValue(tp.x_shear)
        self.y_shear_spin.setValue(tp.y_shear)
        self.x_scale_spin.setValue(tp.x_scale)
        self.y_scale_spin.setValue(tp.y_scale)

