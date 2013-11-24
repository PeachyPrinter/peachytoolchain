import pprint
import ast
from . import tuning_parameters

class TuningParameterFileHandler(object):
    @classmethod
    def write_to_file(cls, tuning_parameters, out_filepath):
        tp = tuning_parameters
        out_dict = {'x_offset': tp.x_offset,
                    'y_offset': tp.y_offset,
                    'x_scale': tp.x_scale,
                    'y_scale': tp.y_scale}
        printer = pprint.PrettyPrinter(indent=4)
        with open(out_filepath, 'w') as out_file:
            out_file.write(printer.pformat(out_dict))

    @classmethod
    def read_from_file(cls, in_filepath):
        with open(in_filepath, 'r') as in_file:
            in_dict = ast.literal_eval(in_file.read())
        if not isinstance(in_dict, dict):
            raise TypeError('Contents of file %s is not a dict' % in_filepath)
        tp = tuning_parameters.TuningParameters()
        tp.x_offset = in_dict['x_offset']
        tp.y_offset = in_dict['y_offset']
        tp.x_scale = in_dict['x_scale']
        tp.y_scale = in_dict['y_scale']
        return tp