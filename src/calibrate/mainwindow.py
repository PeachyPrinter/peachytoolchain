from PySide import QtCore, QtGui
import os.path

from .ui_mainwindow import Ui_MainWindow
from audio.tuning_parameter_file import TuningParameterFileHandler
from audio.tuning_parameters import TuningParameters


class TuningParameterListModel(QtCore.QAbstractListModel):
    def __init__(self, tuning_parameter_collection):
        QtCore.QAbstractListModel.__init__(self)
        self._collection = tuning_parameter_collection

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self._collection.tuning_parameters)

    def index(self, row, col=0, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return QtCore.QModelIndex()
        tp = self._collection.tuning_parameters[row]
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
    def __init__(self, tuning_parameter_collection, audio_server, transformer_proxy, generators, height_adapter, sampling_rate):
        QtGui.QMainWindow.__init__(self)
        self.tuning_collection = tuning_parameter_collection # The collection of all stored tuning parameters
        self.tuning_parameters = tuning_parameter_collection.tuning_parameters[0] # The current tuning parameters
        self.audio_server = audio_server
        self.transformer_proxy = transformer_proxy
        self.generators = generators
        self.generator = None
        self.height_adapter = height_adapter
        self.sampling_rate = sampling_rate
        self.test_height = 0.0
        self.calibrate_test_mode = self.CALIBRATE_MODE
        self.setupUi(self)

        # FIXME: Have to manually add button group because pyside-uic fails to compile them
        self.modulation_buttonGroup = QtGui.QButtonGroup(self)
        self.modulation_buttonGroup.setExclusive(True)
        self.modulation_buttonGroup.addButton(self.modulation_radioButton_AM, 1)
        self.modulation_buttonGroup.addButton(self.modulation_radioButton_DC, 2)

        self.generator_list_model = QtGui.QStringListModel()
        self.generator_list_model.setStringList(sorted(self.generators.keys()))
        self.calibrations_list_model = TuningParameterListModel(self.tuning_collection)
        # Set model now so selection model will be ready for signal creation
        self.calibrations_listview.setModel(self.calibrations_list_model)

        self.build_x_min_edit.editingFinished.connect(self.build_x_min_changed)
        self.build_x_max_edit.editingFinished.connect(self.build_x_max_changed)
        self.build_y_min_edit.editingFinished.connect(self.build_y_min_changed)
        self.build_y_max_edit.editingFinished.connect(self.build_y_max_changed)
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
        self.speed_edit.editingFinished.connect(self.speed_changed)
        self.size_edit.editingFinished.connect(self.size_changed)
        self.shape_center_x_edit.editingFinished.connect(self.shape_center_x_changed)
        self.shape_center_y_edit.editingFinished.connect(self.shape_center_y_changed)
        self.save_button.clicked.connect(self.save_clicked)
        self.load_button.clicked.connect(self.load_clicked)
        self.calibrations_listview.selectionModel().selectionChanged.connect(self.calibration_selection_changed)
        self.tuning_height_edit.editingFinished.connect(self.tuning_height_changed)
        self.add_calibration_button.pressed.connect(self.add_calibration_pressed)
        self.delete_calibration_button.pressed.connect(self.delete_calibration_pressed)
        self.calibrate_here_button.pressed.connect(self.calibrate_here_pressed)
        self.calibrate_test_tab_widget.currentChanged.connect(self.calibrate_test_tab_changed)
        self.test_height_edit.editingFinished.connect(self.test_height_changed)

        self.test_height_edit.setText(str(self.test_height))
        self.calibrate_test_tab_widget.setCurrentWidget(self.calibrate_test_tab_widget.widget(self.calibrate_test_mode))
        self.update_build_parameters()
        index = self.calibrations_list_model.index(0)
        self.calibrations_listview.setCurrentIndex(index)
        self.update_values_from_tuning_parameters()
        # Wait until after connecting signals to connect this model so that signals fire
        self.pattern_combobox.setModel(self.generator_list_model)
        self.pattern_combobox.setCurrentIndex(0)

    def build_x_min_changed(self):
        value = self.build_x_min_edit.text()
        try:
            x_min = float(value)
        except ValueError:
            # Invalid value entered -- reset
            x_min = self.tuning_collection.build_x_min
            self.build_x_min_edit.setText(str(x_min))
        self.tuning_collection.build_x_min = x_min

    def build_x_max_changed(self):
        value = self.build_x_max_edit.text()
        try:
            x_max = float(value)
        except ValueError:
            # Invalid value entered -- reset
            x_max = self.tuning_collection.build_x_max
            self.build_x_max_edit.setText(x_max)
        self.tuning_collection.build_x_max = x_max

    def build_y_min_changed(self):
        value = self.build_y_min_edit.text()
        try:
            y_min = float(value)
        except ValueError:
            # Invalid value entered -- reset
            y_min = self.tuning_collection.build_y_min
            self.build_y_min_edit.setText(str(y_min))
        self.tuning_collection.build_y_min = y_min

    def build_y_max_changed(self):
        value = self.build_y_max_edit.text()
        try:
            y_max = float(value)
        except ValueError:
            # Invalid value entered -- reset
            y_max = self.tuning_collection.build_y_max
            self.build_y_max_edit.setText(str(y_max))
        self.tuning_collection.build_y_max = y_max

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
                self.get_speed(),
                self.get_size(),
                self.get_shape_center()
        )
        self.height_adapter.generator = self.generator

    def speed_changed(self):
        self.generator.speed = self.get_speed()

    def get_speed(self):
        try:
            speed = float(self.speed_edit.text())
        except ValueError:
            # Invalid value entered -- reset
            speed = self.generator.speed
            self.speed_edit.setText(str(speed))
        return speed

    def size_changed(self):
        self.generator.size = self.get_size()

    def get_size(self):
        try:
            size = float(self.size_edit.text())
        except ValueError:
            # Invalid value entered -- reset
            size = self.generator.size
            self.side_edit.setText(str(size))
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
        return (x, y)

    def save_clicked(self):
        (filename, selected_filter) = QtGui.QFileDialog.getSaveFileName(
            self.centralwidget, #parent
            "Save tuning parameters", #caption
        )
        if not filename:
            return
        TuningParameterFileHandler.write_to_file(self.tuning_collection, filename)

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
        self.delete_calibration_button.setEnabled(self.calibrations_list_model.rowCount() > 1)
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

    def test_height_changed(self):
        try:
            height = float(self.test_height_edit.text())
        except ValueError:
            # Invalid value entered -- reset
            height = self.test_height
            self.test_height_edit.setText(str(height))
        self.test_height = height
        self.update_height_adapter()

    def update_height_adapter(self):
        if self.calibrate_test_mode == self.CALIBRATE_MODE:
            self.height_adapter.height = self.tuning_parameters.height
        elif self.calibrate_test_mode == self.TEST_MODE:
            self.height_adapter.height = self.test_height
