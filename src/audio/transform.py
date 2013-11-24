import math

class AudioTransformer(object):
    def __init__(self, tuning_parameters):
        self.tuning_parameters = tuning_parameters

    def transform_values(self, old_values):
        new_values = []
        for left, right in old_values:
            left, right = ((left + right*self.tuning_parameters.x_shear),
                           (right + left*self.tuning_parameters.y_shear))
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
            new_values.append((left, right))
        return new_values
