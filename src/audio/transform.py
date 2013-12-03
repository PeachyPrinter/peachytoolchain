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
            left, right = x, y
            left, right = ((left + x*self.tuning_parameters.x_shear),
                           (right + y*self.tuning_parameters.y_shear))
            left, right = ((left*(1+(y*self.tuning_parameters.x_trapezoid))),
                           (right*(1+(x*self.tuning_parameters.y_trapezoid))))
            left, right = ((left  *  math.cos(self.tuning_parameters.rotation*math.pi/180.0) +
                            right *  math.sin(self.tuning_parameters.rotation*math.pi/180.0)),
                           (left  * -math.sin(self.tuning_parameters.rotation*math.pi/180.0) +
                            right *  math.cos(self.tuning_parameters.rotation*math.pi/180.0)))
            left *= self.tuning_parameters.x_scale
            right *= self.tuning_parameters.y_scale
            left += self.tuning_parameters.x_offset
            right += self.tuning_parameters.y_offset
            left = min(1.0, max(-1.0, left))
            right = min(1.0, max(-1.0, right))
            audio_values.append((left, right))
        return audio_values

