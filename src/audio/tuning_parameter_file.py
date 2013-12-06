import pprint
import ast
from . import tuning_parameters

class TuningParameterFileHandler(object):
    @classmethod
    def write_to_file(cls, tuning_parameter_collection, out_filepath):
        tpc = tuning_parameter_collection
        out_tpc_dict = {
            'build_x_min': tpc.build_x_min,
            'build_x_max': tpc.build_x_max,
            'build_y_min': tpc.build_y_min,
            'build_y_max': tpc.build_y_max,
        }
        tp_list = []
        for tp in tpc.tuning_parameters:
            out_tp_dict = {
                'height': tp.height,
                'x_offset': tp.x_offset,
                'y_offset': tp.y_offset,
                'x_scale': tp.x_scale,
                'y_scale': tp.y_scale,
                'rotation': tp.rotation,
                'x_shear': tp.x_shear,
                'y_shear': tp.y_shear,
                'x_trapezoid': tp.x_trapezoid,
                'y_trapezoid': tp.y_trapezoid,
            }
            tp_list.append(out_tp_dict)
        out_tpc_dict['tuning_parameters'] = tp_list

        printer = pprint.PrettyPrinter(indent=4)
        with open(out_filepath, 'w') as out_file:
            out_file.write(printer.pformat(out_tpc_dict))

    @classmethod
    def read_from_file(cls, in_filepath):
        with open(in_filepath, 'r') as in_file:
            in_dict = ast.literal_eval(in_file.read())
        if not isinstance(in_dict, dict):
            raise TypeError('Contents of file %s is not a dict' % in_filepath)
        tpc = tuning_parameters.TuningParameterCollection()
        tpc.build_x_min = in_dict['build_x_min']
        tpc.build_x_max = in_dict['build_x_max']
        tpc.build_y_min = in_dict['build_y_min']
        tpc.build_y_max = in_dict['build_y_max']
        tp_dicts = in_dict['tuning_parameters']
        tps = []
        for in_tp_dict in tp_dicts:
            tp = tuning_parameters.TuningParameters()
            tp.height = in_tp_dict['height']
            tp.x_offset = in_tp_dict['x_offset']
            tp.y_offset = in_tp_dict['y_offset']
            tp.x_scale = in_tp_dict['x_scale']
            tp.y_scale = in_tp_dict['y_scale']
            tp.rotation = in_tp_dict['rotation']
            tp.x_shear = in_tp_dict['x_shear']
            tp.y_shear = in_tp_dict['y_shear']
            tp.x_trapezoid = in_tp_dict['x_trapezoid']
            tp.y_trapezoid = in_tp_dict['y_trapezoid']
            tps.append(tp)
        tpc.tuning_parameters = tps
        return tpc