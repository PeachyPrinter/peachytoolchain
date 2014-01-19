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
        audio_values = []
        x_min = self.tuning_parameter_collection.build_x_min
        x_max = self.tuning_parameter_collection.build_x_max
        y_min = self.tuning_parameter_collection.build_y_min
        y_max = self.tuning_parameter_collection.build_y_max
        x_size = x_max - x_min
        y_size = y_max - y_min
        # Edge case: fail gracefully if 0 size
        if x_size == 0 or y_size == 0:
            return [(0.0, 0.0) for i in range(len(points))]
        # Optimization: assume Z stays relatively constant while X and Y changes. Split samples into chunks where
        # Z is constant in each chunk. Process each chunk at constant Z.
        start_i = 0
        while start_i < len(points):
            cur_z = points[start_i][2]
            end_i = start_i
            # Find the length of the current constant-Z chunk
            while end_i < len(points):
                if points[end_i][2] != cur_z:
                    # Z has changed; process the preceeding chunk of points
                    break
                end_i += 1
            # Transform chunk of points to audio values
            tp = self.tuning_parameter_collection.get_tuning_parameters_for_height(cur_z)
            audio = [(
                        ((-1.0 + 2.0 * (points[i][0] - x_min) / x_size) + tp.x_offset) * tp.x_scale,
                        ((-1.0 + 2.0 * (points[i][1] - y_min) / y_size) + tp.y_offset) * tp.y_scale
                     ) for i in range(start_i, end_i)]
            rot_l_l = math.cos(tp.rotation*math.pi/180.0)
            rot_l_r = math.sin(tp.rotation*math.pi/180.0)
            rot_r_l = -math.sin(tp.rotation*math.pi/180.0)
            rot_r_r = math.cos(tp.rotation*math.pi/180.0)
            audio = [(
                         audio[i][0] * rot_l_l + audio[i][1] * rot_l_r,
                         audio[i][0] * rot_r_l + audio[i][1] * rot_r_r
                     ) for i in range(len(audio))]
            audio = [(
                         audio[i][0] + audio[i][1] * tp.x_shear,
                         audio[i][1] + audio[i][0] * tp.y_shear
                     ) for i in range(len(audio))]
            audio = [(
                         audio[i][0] * (1 + audio[i][1] * tp.x_trapezoid),
                         audio[i][1] * (1 + audio[i][0] * tp.y_trapezoid)
                     ) for i in range(len(audio))]
            audio_values.extend(audio)
            start_i = end_i
        return audio_values

