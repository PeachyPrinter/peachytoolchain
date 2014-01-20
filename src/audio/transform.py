import math
import numpy

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
        assert isinstance(points, numpy.ndarray)
        num_points = points.shape[0]
        assert points.shape[1] == 3
        audio = numpy.empty((num_points, 2), dtype=numpy.float)
        x_min = self.tuning_parameter_collection.build_x_min
        x_max = self.tuning_parameter_collection.build_x_max
        y_min = self.tuning_parameter_collection.build_y_min
        y_max = self.tuning_parameter_collection.build_y_max
        x_size = x_max - x_min
        y_size = y_max - y_min
        # Edge case: fail gracefully if 0 size
        if x_size == 0 or y_size == 0:
            #return [(0.0, 0.0) for i in range(len(points))]
            return numpy.zeros((num_points, 2))
        # Optimization: assume Z stays relatively constant while X and Y changes. Split samples into chunks where
        # Z is constant in each chunk. Process each chunk at constant Z.
        chunk_breaks = [0] + ((points[1:,2] - points[:-1,2]).nonzero()[0]+1).tolist() + [num_points]
        for chunk_i in range(len(chunk_breaks)-1):
            # Transform chunk of points to audio values
            start_i = chunk_breaks[chunk_i]
            end_i = chunk_breaks[chunk_i+1]
            cur_z = points[start_i][2]
            tp = self.tuning_parameter_collection.get_tuning_parameters_for_height(cur_z)
            audio[start_i:end_i,0] = ((((points[start_i:end_i,0] - x_min) / x_size) * 2.0 - 1.0) + tp.x_offset) * tp.x_scale
            audio[start_i:end_i,1] = ((((points[start_i:end_i,1] - y_min) / y_size) * 2.0 - 1.0) + tp.y_offset) * tp.y_scale
            rot_l_l = math.cos(tp.rotation*math.pi/180.0)
            rot_l_r = math.sin(tp.rotation*math.pi/180.0)
            rot_r_l = -math.sin(tp.rotation*math.pi/180.0)
            rot_r_r = math.cos(tp.rotation*math.pi/180.0)
            rotate_matrix = numpy.array([[rot_l_l, rot_l_r],
                                         [rot_r_l, rot_r_r]]).T
            audio[start_i:end_i,:] = numpy.dot(audio[start_i:end_i,:], rotate_matrix)
            shear_matrix = numpy.array([[1, tp.x_shear],
                                        [tp.y_shear, 1]]).T
            audio[start_i:end_i,:] = numpy.dot(audio[start_i:end_i,:], shear_matrix)
            #:TODO: Add trapezoid. It's not an affine transformation, so requires a 3x3 homogeneous matrix solution.
        return audio

