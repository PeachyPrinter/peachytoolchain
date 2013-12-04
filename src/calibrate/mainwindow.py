from PySide import QtCore, QtGui
import os
import os.path

from .ui_mainwindow import Ui_MainWindow
from audio.tuning_parameter_file import TuningParameterFileHandler

class MainWindow(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self, tuning_parameters, audio_server, transformer_proxy, generators, height_adapter, sampling_rate):
        QtGui.QMainWindow.__init__(self)
        self.tuning_parameters = tuning_parameters
        self.audio_server = audio_server
        self.transformer_proxy = transformer_proxy
        self.generators = generators
        self.generator = None
        self.height_adapter = height_adapter
        self.sampling_rate = sampling_rate
        self.setupUi(self)
        self.setup_signals()
        self.setup_models()
        self.setup_initial_values()

    def setup_signals(self):
        self.build_x_min_edit.textChanged.connect(self.build_x_min_changed)
        self.build_x_max_edit.textChanged.connect(self.build_x_max_changed)
        self.build_y_min_edit.textChanged.connect(self.build_y_min_changed)
        self.build_y_max_edit.textChanged.connect(self.build_y_max_changed)
        self.x_offset_spin.valueChanged.connect(self.x_offset_changed)
        self.y_offset_spin.valueChanged.connect(self.y_offset_changed)
        self.x_scale_spin.valueChanged.connect(self.x_scale_changed)
        self.y_scale_spin.valueChanged.connect(self.y_scale_changed)
        self.rotation_spin.valueChanged.connect(self.rotation_changed)
        self.x_shear_spin.valueChanged.connect(self.x_shear_changed)
        self.y_shear_spin.valueChanged.connect(self.y_shear_changed)
        self.x_trapezoid_spin.valueChanged.connect(self.x_trapezoid_changed)
        self.y_trapezoid_spin.valueChanged.connect(self.y_trapezoid_changed)
        self.pattern_combobox.currentIndexChanged.connect(self.pattern_changed)
        self.speed_edit.textChanged.connect(self.speed_changed)
        self.size_edit.textChanged.connect(self.size_changed)
        self.shape_center_x_edit.textChanged.connect(self.shape_center_x_changed)
        self.shape_center_y_edit.textChanged.connect(self.shape_center_y_changed)
        self.save_button.clicked.connect(self.save_clicked)
        self.load_button.clicked.connect(self.load_clicked)

    def build_x_min_changed(self, value):
        try:
            x_min = float(value)
        except ValueError:
            x_min = 0.0
        self.tuning_parameters.build_x_min = x_min

    def build_x_max_changed(self, value):
        try:
            x_max = float(value)
        except ValueError:
            x_max = 1.0
        self.tuning_parameters.build_x_max = x_max

    def build_y_min_changed(self, value):
        try:
            y_min = float(value)
        except ValueError:
            y_min = 0.0
        self.tuning_parameters.build_y_min = y_min

    def build_y_max_changed(self, value):
        try:
            y_max = float(value)
        except ValueError:
            y_max = 1.0
        self.tuning_parameters.build_y_max = y_max

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

    def x_trapezoid_changed(self, value):
        self.tuning_parameters.x_trapezoid = value

    def y_trapezoid_changed(self, value):
        self.tuning_parameters.y_trapezoid = value

    def setup_models(self):
        self.generator_list_model = QtGui.QStringListModel()
        self.generator_list_model.setStringList(sorted(self.generators.keys()))

    def setup_initial_values(self):
        self.pattern_combobox.setModel(self.generator_list_model)
        self.pattern_combobox.setCurrentIndex(0)
        self._update_tuning_parameters()

    def pattern_changed(self, index):
        pattern_name = self.generator_list_model.data(
            self.generator_list_model.index(index),
            QtCore.Qt.DisplayRole
        )
        self.generator = self.generators[pattern_name](
                self.sampling_rate,
                self.get_speed(),
                self.get_size(),
                self.get_shape_center()
        )
        self.height_adapter.generator = self.generator

    def speed_changed(self, value):
        self.generator.speed = self.get_speed()

    def get_speed(self):
        try:
            speed = float(self.speed_edit.text())
        except ValueError:
            speed = 1.0
        return speed

    def size_changed(self, value):
        self.generator.size = self.get_size()

    def get_size(self):
        try:
            size = float(self.size_edit.text())
        except ValueError:
            size = 1.0
        return size

    def shape_center_x_changed(self, value):
        self.generator.center = self.get_shape_center()

    def shape_center_y_changed(self, value):
        self.generator.center = self.get_shape_center()

    def get_shape_center(self):
        try:
            x = float(self.shape_center_x_edit.text())
        except ValueError:
            x = 0.0
        try:
            y = float(self.shape_center_y_edit.text())
        except ValueError:
            y = 0.0
        return (x, y)

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
        self.build_x_min_edit.setText(str(tp.build_x_min))
        self.build_x_max_edit.setText(str(tp.build_x_max))
        self.build_y_min_edit.setText(str(tp.build_y_min))
        self.build_y_max_edit.setText(str(tp.build_y_max))
        self.x_offset_spin.setValue(tp.x_offset)
        self.y_offset_spin.setValue(tp.y_offset)
        self.rotation_spin.setValue(tp.rotation)
        self.x_shear_spin.setValue(tp.x_shear)
        self.y_shear_spin.setValue(tp.y_shear)
        self.x_scale_spin.setValue(tp.x_scale)
        self.y_scale_spin.setValue(tp.y_scale)
        self.x_trapezoid_spin.setValue(tp.x_trapezoid)
        self.y_trapezoid_spin.setValue(tp.y_trapezoid)

