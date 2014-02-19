from PySide import QtCore, QtGui
import os.path
import threading

from .ui_mainwindow import Ui_MainWindow
from audio.tuning_parameter_file import TuningParameterFileHandler
from audio.modulation import ModulationTypes, getModulator


class TuningParameterListModel(QtCore.QAbstractListModel):
    def __init__(self, tuning_parameter_collection):
        QtCore.QAbstractListModel.__init__(self)
        self._collection = tuning_parameter_collection

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self._collection.tuning_parameters)

    def index(self, row, col=0, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return QtCore.QModelIndex()
        return self.createIndex(row, col, None)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None
        if index.parent().isValid():
            return None
        if index.column() > 0:
            return None
        row = index.row()
        if row < 0 or row > len(self._collection.tuning_parameters):
            return None
        tp = self._collection.tuning_parameters[index.row()]
        if role == QtCore.Qt.UserRole:
            return tp
        if role == QtCore.Qt.DisplayRole:
            return str(tp.height)
        return None

    def headerData(self, col, orientation, role=QtCore.Qt.DisplayRole):
        if col > 0:
            return None
        if orientation != QtCore.Qt.Horizontal:
            return None
        if role == QtCore.Qt.DisplayRole:
            return 'Height'
        return None

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if not index.isValid():
            return False
        if role != QtCore.Qt.EditRole:
            return False
        if index.column() > 0:
            return False
        row = index.row()
        if row < 0 or row >= len(self._collection.tuning_parameters):
            return False
        tp = self._collection.tuning_parameters[row]
        tp.height = float(value)
        self.dataChanged.emit(index, index)
        return True

    def removeRow(self, row, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return False
        if row < 0 or row >= len(self._collection.tuning_parameters):
            return False
        self.beginRemoveRows(parent, row, row)
        del self._collection.tuning_parameters[row]
        self.endRemoveRows()

    def addRow(self, tp):
        num_rows = self.rowCount()
        self.beginInsertRows(QtCore.QModelIndex(), num_rows, num_rows)
        self._collection.tuning_parameters.append(tp)
        self.endInsertRows()


class MainWindow(QtGui.QMainWindow, Ui_MainWindow):
    CALIBRATE_MODE = 0
    TEST_MODE = 1
    MODULATION_TYPE_BY_ID = {1: ModulationTypes.AM,
                             2: ModulationTypes.DC}
    MODULATION_ID_BY_TYPE = dict((v, k) for (k, v) in MODULATION_TYPE_BY_ID.items())
    LASER_POWER_ON_ID = 1
    LASER_POWER_OFF_ID = 0

    def __init__(self, tuning_parameter_collection, audio_server, modulator_proxy, transformer_proxy, generators,
                 height_adapter, sampling_rate):
        QtGui.QMainWindow.__init__(self)
        self.tuning_collection = tuning_parameter_collection  # The collection of all stored tuning parameters
        self.tuning_parameters = tuning_parameter_collection.tuning_parameters[0]  # The current tuning parameters
        self.audio_server = audio_server
        self.modulator_proxy = modulator_proxy
        self.transformer_proxy = transformer_proxy
        self.generators = generators
        self.generator = None
        self.height_adapter = height_adapter
        self.sampling_rate = sampling_rate
        self.test_height = 0.0
        self.calibrate_test_mode = self.CALIBRATE_MODE
        self.laser_enabled = True
        self.setupUi(self)

        # NOTE: Have to manually add button group because pyside-uic fails to compile them
        self.modulation_buttonGroup = QtGui.QButtonGroup(self)
        self.modulation_buttonGroup.setExclusive(True)
        self.modulation_buttonGroup.addButton(self.modulation_radioButton_AM,
                                              self.MODULATION_ID_BY_TYPE[ModulationTypes.AM])
        self.modulation_buttonGroup.addButton(self.modulation_radioButton_DC,
                                              self.MODULATION_ID_BY_TYPE[ModulationTypes.DC])
        self.laser_power_buttonGroup = QtGui.QButtonGroup(self)
        self.laser_power_buttonGroup.setExclusive(True)
        self.laser_power_buttonGroup.addButton(self.laser_power_radioButton_On, self.LASER_POWER_ON_ID)
        self.laser_power_buttonGroup.addButton(self.laser_power_radioButton_Off, self.LASER_POWER_OFF_ID)

        self.generator_list_model = QtGui.QStringListModel()
        self.generator_list_model.setStringList(sorted(self.generators.keys()))
        self.calibrations_list_model = TuningParameterListModel(self.tuning_collection)
        # Set model now so selection model will be ready for signal creation
        self.calibrations_listview.setModel(self.calibrations_list_model)

        self.build_x_min_edit.editingFinished.connect(
            self.make_edit_signal_handler(self.build_x_min_edit, self.tuning_collection, 'build_x_min')
        )
        self.build_y_min_edit.editingFinished.connect(
            self.make_edit_signal_handler(self.build_y_min_edit, self.tuning_collection, 'build_y_min')
        )
        self.build_x_max_edit.editingFinished.connect(
            self.make_edit_signal_handler(self.build_x_max_edit, self.tuning_collection, 'build_x_max')
        )
        self.build_y_max_edit.editingFinished.connect(
            self.make_edit_signal_handler(self.build_y_max_edit, self.tuning_collection, 'build_y_max')
        )
        self.dwell_x_edit.editingFinished.connect(
            self.make_edit_signal_handler(self.dwell_x_edit, self.tuning_collection, 'dwell_x')
        )
        self.dwell_y_edit.editingFinished.connect(
            self.make_edit_signal_handler(self.dwell_y_edit, self.tuning_collection, 'dwell_y')
        )
        self.velocity_x_max_edit.editingFinished.connect(
            self.make_edit_signal_handler(self.velocity_x_max_edit, self.tuning_collection, 'velocity_x_max',
                                      lambda x: x > 0)
        )
        self.velocity_y_max_edit.editingFinished.connect(
            self.make_edit_signal_handler(self.velocity_y_max_edit, self.tuning_collection, 'velocity_y_max',
                                      lambda x: x > 0)
        )
        self.drips_per_height_edit.editingFinished.connect(
            self.make_edit_signal_handler(self.drips_per_height_edit, self.tuning_collection, 'drips_per_height',
                                      lambda x: x > 0)
        )
        self.sublayer_height_edit.editingFinished.connect(
            self.make_edit_signal_handler(self.sublayer_height_edit, self.tuning_collection, 'sublayer_height',
                                      lambda x: x > 0)
        )

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
        self.speed_edit.valueChanged.connect(self.speed_changed)
        self.size_edit.valueChanged.connect(self.size_changed)
        ramp_speed = self.ramp_speed.stateChanged # Seg Fault Workaround
        self.ramp_speed.stateChanged.connect(self.ramp_speed_checked)
        self.ramp_speed_time.valueChanged.connect(self.ramp_speed_time_changed)
        self.shape_center_x_edit.editingFinished.connect(self.shape_center_x_changed)
        self.shape_center_y_edit.editingFinished.connect(self.shape_center_y_changed)
        self.save_button.clicked.connect(self.save_clicked)
        self.load_button.clicked.connect(self.load_clicked)

        calibrations_listview_selection_model = self.calibrations_listview.selectionModel() # Seg fault workaround
        self.calibrations_listview.selectionModel().selectionChanged.connect(self.calibration_selection_changed)

        self.tuning_height_edit.editingFinished.connect(self.tuning_height_changed)
        self.add_calibration_button.pressed.connect(self.add_calibration_pressed)
        self.delete_calibration_button.pressed.connect(self.delete_calibration_pressed)
        self.calibrate_here_button.pressed.connect(self.calibrate_here_pressed)
        self.calibrate_test_tab_widget.currentChanged.connect(self.calibrate_test_tab_changed)
        self.test_height_edit.editingFinished.connect(
            self.make_edit_signal_handler(self.test_height_edit, self, 'test_height', lambda x: x>=0,
                                      self.update_height_adapter)
        )
        #noinspection PyUnresolvedReferences
        self.modulation_buttonGroup.buttonClicked[int].connect(self.modulation_changed)
        #noinspection PyUnresolvedReferences
        self.laser_power_buttonGroup.buttonClicked[int].connect(self.laser_power_changed)

        self.test_height_edit.setText(str(self.test_height))
        self.calibrate_test_tab_widget.setCurrentWidget(self.calibrate_test_tab_widget.widget(self.calibrate_test_mode))
        self.update_build_parameters()
        index = self.calibrations_list_model.index(0)
        self.calibrations_listview.setCurrentIndex(index)
        self.update_values_from_tuning_parameters()
        # Wait until after connecting signals to connect this model so that signals fire
        self.pattern_combobox.setModel(self.generator_list_model)
        self.pattern_combobox.setCurrentIndex(0)
        self.modulation_radioButton_AM.setChecked(True)
        self.laser_power_radioButton_On.setChecked(True)
        self.tuning_parameters = self.tuning_collection.get_tuning_parameters_for_height(0.0)
        
        

    def make_edit_signal_handler(self, edit, container, var_name, validator=None, after=None):
        def fn():
            self._parse_edit_as_float(edit, container, var_name, validator, after)
        return fn

    def _parse_edit_as_float(self, edit, container, var_name, validator=None, after=None):
        text = edit.text()
        valid = True
        value = None
        try:
            value = float(text)
        except ValueError:
            valid = False
        if valid and validator:
            valid = validator(value)
        if not valid:
            # Reset editbox with original value of var
            value = getattr(container, var_name)
        else:
            # Save value on container
            setattr(container, var_name, value)
            # Update editbox to use proper string of the parsed float value
        text = str(value)
        edit.setText(text)
        if after:
            after()

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

    def pattern_changed(self, index):
        pattern_name = self.generator_list_model.data(
            self.generator_list_model.index(index),
            QtCore.Qt.DisplayRole
        )
        self.generator = self.generators[pattern_name](
            self.sampling_rate,
            int(self.get_speed()),
            self.size_edit.value(),
            self.get_shape_center()
        )
        self.height_adapter.generator = self.generator

    def speed_changed(self):
        self.generator.speed = int(self.get_speed())

    _ramp_speed_interval = None
    _ramp_timer = None
    _ramp_maximum = 100000.0
    def _increase_size(self, amount = 1):
        if (self.generator.speed < self._ramp_maximum and self.ramp_speed.checkState()):
            speed = self.generator.speed + 1
            self.speed_edit.setValue(speed)
            self._ramp_timer = threading.Timer(self._ramp_speed_interval, self._increase_size)
            self._ramp_timer.daemon=True
            self._ramp_timer.start()
        else:
            self.ramp_speed.setCheckState(QtCore.Qt.Unchecked)

    def ramp_speed_checked(self):
        if (self.ramp_speed.checkState()):
            self._ramp_speed_interval = self.ramp_speed_time.value()
            self._increase_size()
        else:
            if (self._ramp_timer):
                self._ramp_timer.cancel()
            self._ramp_timer = None

    def ramp_speed_time_changed(self):
        self._ramp_speed_interval = self.ramp_speed_time.value()

    def get_speed(self):
        try:
            speed = float(self.speed_edit.text())
        except ValueError:
            # Invalid value entered -- reset
            speed = self.generator.speed
            self.speed_edit.setValue(speed)
        if speed <= 0:
            speed = self.generator.speed

        self.speed_edit.setValue(speed)
        return speed

    def size_changed(self):
        self.generator.size = self.get_size()

    def get_size(self):
        try:
            size = float(self.size_edit.text())
        except ValueError:
            # Invalid value entered -- reset
            size = self.generator.size
            self.size_edit.setValue(size)
        if size <= 0:
            size = self.generator.size
        self.size_edit.setValue(size)
        return size

    def shape_center_x_changed(self):
        self.generator.center = self.get_shape_center()

    def shape_center_y_changed(self):
        self.generator.center = self.get_shape_center()

    def get_shape_center(self):
        try:
            x = float(self.shape_center_x_edit.text())
        except ValueError:
            x = None
        try:
            y = float(self.shape_center_y_edit.text())
        except ValueError:
            y = None
        if x is None or y is None:
            # Invalid value entered -- reset
            (x, y) = self.generator.center
        self.shape_center_x_edit.setText(str(x))
        self.shape_center_y_edit.setText(str(y))
        return x, y

    def save_clicked(self):
        (filename, selected_filter) = QtGui.QFileDialog.getSaveFileName(
            self.centralwidget,  # parent
            "Save tuning parameters",  # caption
        )
        if not filename:
            return
        TuningParameterFileHandler.write_to_file(self.tuning_collection, filename)

    def load_clicked(self):
        (filename, selected_filter) = QtGui.QFileDialog.getOpenFileName(
            self.centralwidget,  # parent
            "Open tuning parameter file",  # caption
        )
        if not filename:
            return
        if not os.path.exists(filename):
            #noinspection PyArgumentList
            QtGui.QMessageBox.critical(
                parent=self,
                caption="No such file",
                text="Unable to open file %s: no such file exists." % filename
            )
            return
        tuning_parameters = TuningParameterFileHandler.read_from_file(filename)
        self.calibrations_list_model.beginResetModel()
        self.tuning_collection.update(tuning_parameters)
        self.calibrations_list_model.endResetModel()
        index = self.calibrations_list_model.index(0)
        self.calibrations_listview.setCurrentIndex(index)
        self.update_build_parameters()
        self.update_values_from_tuning_parameters()

    def update_build_parameters(self):
        tpc = self.tuning_collection
        self.build_x_min_edit.setText(str(tpc.build_x_min))
        self.build_x_max_edit.setText(str(tpc.build_x_max))
        self.build_y_min_edit.setText(str(tpc.build_y_min))
        self.build_y_max_edit.setText(str(tpc.build_y_max))
        self.velocity_x_max_edit.setText(str(tpc.velocity_x_max))
        self.velocity_y_max_edit.setText(str(tpc.velocity_y_max))
        self.dwell_x_edit.setText(str(tpc.dwell_x))
        self.dwell_y_edit.setText(str(tpc.dwell_y))
        self.drips_per_height_edit.setText(str(tpc.drips_per_height))
        self.sublayer_height_edit.setText(str(tpc.sublayer_height))
        button_id = self.MODULATION_ID_BY_TYPE[tpc.modulation]
        button = self.modulation_buttonGroup.button(button_id)
        button.setChecked(True)
        # Needs to be updated manually, since signal only triggers on click
        self.modulation_changed(button_id)

    def update_values_from_tuning_parameters(self):
        tp = self.tuning_parameters
        self.tuning_height_edit.setText(str(tp.height))
        self.x_offset_spin.setValue(tp.x_offset)
        self.y_offset_spin.setValue(tp.y_offset)
        self.rotation_spin.setValue(tp.rotation)
        self.x_shear_spin.setValue(tp.x_shear)
        self.y_shear_spin.setValue(tp.y_shear)
        self.x_scale_spin.setValue(tp.x_scale)
        self.y_scale_spin.setValue(tp.y_scale)
        self.x_trapezoid_spin.setValue(tp.x_trapezoid)
        self.y_trapezoid_spin.setValue(tp.y_trapezoid)

    def get_selected_calibration_index(self):
        selection_model = self.calibrations_listview.selectionModel()
        indexes = selection_model.selectedRows()
        if len(indexes) == 1:
            index = indexes[0]
        else:
            index = self.calibrations_list_model.index(0, 0, QtCore.QModelIndex())
            selection_model.select(index, QtGui.QItemSelectionModel.ClearAndSelect)
        return index

    #noinspection PyUnusedLocal
    def calibration_selection_changed(self, selected, deselected):
        index = self.get_selected_calibration_index()
        tp = self.calibrations_list_model.data(index, role=QtCore.Qt.UserRole)
        self.tuning_parameters = tp
        self.update_values_from_tuning_parameters()
        self.update_height_adapter()
        self.delete_calibration_button.setEnabled(self.calibrations_list_model.rowCount() > 1)

    def tuning_height_changed(self):
        indexes = self.calibrations_listview.selectionModel().selectedRows()
        if len(indexes) == 0:
            raise AssertionError('Tuning height changed when no calibration selected')
        index = indexes[0]

        value = self.tuning_height_edit.text()
        try:
            height = float(value)
        except ValueError:
            # Invalid value entered -- reset
            height = self.calibrations_list_model.data(index)
            self.tuning_height_edit.setText(str(height))
        self.calibrations_list_model.setData(index, height)
        self.update_height_adapter()

    def add_calibration_pressed(self):
        (text, ok) = QtGui.QInputDialog.getText(
            self,
            'Add new calibration',
            'Height for new calibration:',
            text='0.0'
        )
        if not ok:
            return
        try:
            height = float(text)
        except ValueError:
            height = None
        if height is None:
            dialog = QtGui.QMessageBox.critical(
                self,
                'Invalid height',
                'Cannot create new calibration. Height must be a number.'
            )
            dialog.exec_()
            return
        tp = self.tuning_collection.get_tuning_parameters_for_height(height)
        self.calibrations_list_model.addRow(tp)
        self.calibrations_listview.selectionModel().select(
            self.calibrations_list_model.index(self.calibrations_list_model.rowCount()-1, 0, QtCore.QModelIndex()),
            QtGui.QItemSelectionModel.ClearAndSelect
        )
        # Selection causes update of current tuning parameters as a side-effect, so no need to do it explicitly here

    def delete_calibration_pressed(self):
        dialog = QtGui.QMessageBox(
            QtGui.QMessageBox.Question,
            'Delete current calibration',
            'Are you sure you want to delete the current calibration point?',
            buttons=QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel,
            parent=self,
        )
        dialog.exec_()
        if dialog.standardButton(dialog.clickedButton()) != QtGui.QMessageBox.Ok:
            return
        index = self.get_selected_calibration_index()
        self.calibrations_list_model.removeRow(index.row())
        self.delete_calibration_button.setEnabled(self.calibrations_list_model.rowCount()>1)
        # Selection causes update of current tuning parameters as a side-effect, so no need to do it explicitly here

    def calibrate_here_pressed(self):
        tp = self.tuning_collection.get_tuning_parameters_for_height(self.test_height)
        self.calibrations_list_model.addRow(tp)
        self.calibrations_listview.selectionModel().select(
            self.calibrations_list_model.index(self.calibrations_list_model.rowCount()-1, 0, QtCore.QModelIndex()),
            QtGui.QItemSelectionModel.ClearAndSelect
        )
        # Selection causes update of current tuning parameters as a side-effect, so no need to do it explicitly here
        self.calibrate_test_tab_widget.setCurrentWidget(
            self.calibrate_test_tab_widget.widget(self.CALIBRATE_MODE)
        )

    def calibrate_test_tab_changed(self, index):
        self.calibrate_test_mode = index
        self.update_height_adapter()

    def update_height_adapter(self):
        if self.calibrate_test_mode == self.CALIBRATE_MODE:
            self.height_adapter.height = self.tuning_parameters.height
        elif self.calibrate_test_mode == self.TEST_MODE:
            self.height_adapter.height = self.test_height

    def modulation_changed(self, button_id):
        modulation_type = self.MODULATION_TYPE_BY_ID[button_id]
        self.tuning_collection.modulation = modulation_type
        modulator = getModulator(modulation_type, self.sampling_rate)
        modulator.laser_enabled = self.laser_enabled
        self.modulator_proxy.modulator = modulator

    def laser_power_changed(self, button_id):
        self.laser_enabled = (button_id == self.LASER_POWER_ON_ID)
        self.modulator_proxy.laser_enabled = self.laser_enabled