import math

class PositionToAudioTransformer(object):
    """
    Utility class for converting position values into audio values based on the tuning values present in the
    tuning parameters.
    """
    def __init__(self, tuning_parameters):
        """
        tuning_parameters -- TuningParameters -- These values will be used to adjust how the transformation is performed.
        """
        self.tuning_parameters = tuning_parameters

    def transform_points(self, points):
        """Transform position coordinates into audio values based on the tuning parameters currently set.
        points -- list of (x, y, z) tuples
        return -- list of (left, right) audio values, which should be +/- 1.0 at the positional bounds
        """
        audio_values = []
        for x, y, z in points:
            build_x_size = self.tuning_parameters.build_x_max - self.tuning_parameters.build_x_min
            build_y_size = self.tuning_parameters.build_y_max - self.tuning_parameters.build_y_min
            if not build_x_size > 0:
                build_x_size = 1.0
            if not build_y_size > 0:
                build_y_size = 1.0
            left = -1.0 + 2.0 * (x - self.tuning_parameters.build_x_min) / build_x_size
            right = -1.0 + 2.0 * (y - self.tuning_parameters.build_y_min) / build_y_size
            left += self.tuning_parameters.x_offset
            right += self.tuning_parameters.y_offset
            left *= self.tuning_parameters.x_scale
            right *= self.tuning_parameters.y_scale
            left, right = ((left  *  math.cos(self.tuning_parameters.rotation*math.pi/180.0) +
                            right *  math.sin(self.tuning_parameters.rotation*math.pi/180.0)),
                           (left  * -math.sin(self.tuning_parameters.rotation*math.pi/180.0) +
                            right *  math.cos(self.tuning_parameters.rotation*math.pi/180.0)))
            left, right = ((left + right*self.tuning_parameters.x_shear),
                           (right + left*self.tuning_parameters.y_shear))
            left, right = ((left*(1+(right*self.tuning_parameters.x_trapezoid))),
                           (right*(1+(left*self.tuning_parameters.y_trapezoid))))
            audio_values.append((left, right))
        return audio_values

