import math

class PositionToAudioTransformer(object):
    """
    Utility class for converting position values into audio values based on the tuning values present in the
    tuning parameters.
    """
    def __init__(self, tuning_parameter_collection):
        """
        tuning_parameter_collection -- TuningParameterCollection -- These values will be used to adjust how the
            transformation is performed.
        """
        self.tuning_parameter_collection = tuning_parameter_collection

    def transform_points(self, points):
        """Transform position coordinates into audio values based on the tuning parameters currently set.
        points -- list of (x, y, z) tuples
        return -- list of (left, right) audio values, which should be +/- 1.0 at the positional bounds
        """
        last_z = None
        last_tp = None
        audio_values = []
        for x, y, z in points:
            # Scale X/Y to audio based on build area
            build_x_size = self.tuning_parameter_collection.build_x_max - self.tuning_parameter_collection.build_x_min
            build_y_size = self.tuning_parameter_collection.build_y_max - self.tuning_parameter_collection.build_y_min
            if not build_x_size > 0:
                build_x_size = 1.0
            if not build_y_size > 0:
                build_y_size = 1.0
            left = -1.0 + 2.0 * (x - self.tuning_parameter_collection.build_x_min) / build_x_size
            right = -1.0 + 2.0 * (y - self.tuning_parameter_collection.build_y_min) / build_y_size
            # Adjust based on tuning parameters at this height
            if z != last_z:
                tp = self.tuning_parameter_collection.get_tuning_parameters_for_height(z)
                last_tp = tp
            else:
                tp = last_tp
            left += tp.x_offset
            right += tp.y_offset
            left *= tp.x_scale
            right *= tp.y_scale
            left, right = ((left  *  math.cos(tp.rotation*math.pi/180.0) +
                            right *  math.sin(tp.rotation*math.pi/180.0)),
                           (left  * -math.sin(tp.rotation*math.pi/180.0) +
                            right *  math.cos(tp.rotation*math.pi/180.0)))
            left, right = ((left + right*tp.x_shear),
                           (right + left*tp.y_shear))
            left, right = ((left*(1+(right*tp.x_trapezoid))),
                           (right*(1+(left*tp.y_trapezoid))))
            audio_values.append((left, right))
        return audio_values

