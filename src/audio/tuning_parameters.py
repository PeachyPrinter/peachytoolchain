class TuningParameterCollection(object):
    """
    Holds multiple tuning parameters at various heights. Each acts as a calibration point.
    """
    tuning_parameters = []
    build_x_min = -1.0
    build_x_max = 1.0
    build_y_min = -1.0
    build_y_max = 1.0

    def __init__(self):
        self.tuning_parameters = [TuningParameters(),]

    def get_tuning_parameters_for_height(self, height):
        # Edge cases
        new_tp = TuningParameters()
        if not self.tuning_parameters:
            return new_tp
        tps = sorted(self.tuning_parameters, key=lambda tp: tp.height)
        lower_tp = None
        higher_tp = None
        for tp in tps:
            if tp.height == height:
                new_tp.update(tp)
                return new_tp
            elif tp.height < height:
                lower_tp = tp
            elif tp.height > height:
                higher_tp = tp
                break
        if lower_tp is None:
            new_tp.update(higher_tp)
            new_tp.height = height
            return new_tp
        if higher_tp is None:
            new_tp.update(lower_tp)
            new_tp.height = height
            return new_tp
        ratio = (height - lower_tp.height)/(higher_tp.height - lower_tp.height)
        for attr in new_tp.__dict__.keys():
            if attr.startswith('_'):
                continue
            setattr(new_tp, attr, getattr(lower_tp, attr)*(1.0-ratio) + getattr(higher_tp, attr)*ratio)
        new_tp.height = height
        return new_tp

    def update(self, other):
        self.build_x_min = other.build_x_min
        self.build_x_max = other.build_x_max
        self.build_y_min = other.build_y_min
        self.build_y_max = other.build_y_max
        self.tuning_parameters = []
        for other_tp in other.tuning_parameters:
            my_tp = TuningParameters()
            my_tp.update(other_tp)
            self.tuning_parameters.append(my_tp)


class TuningParameters(object):
    """
    Coefficients that modify the transformation from position to audio output. All values are valid only for a single
    height. To handle multiple heights, the TuningParameterCollection must be used.
    """
    def __init__(self):
        self.height = 0.0
        self.x_offset = 0.0
        self.y_offset = 0.0
        self.rotation = 0.0
        self.x_shear = 0.0
        self.y_shear = 0.0
        self.x_scale = 1.0
        self.y_scale = 1.0
        self.x_trapezoid = 0.0
        self.y_trapezoid = 0.0

    def update(self, other):
        """Copy the values from another instance."""
        self.height = other.height
        self.x_offset = other.x_offset
        self.y_offset = other.y_offset
        self.rotation = other.rotation
        self.x_shear = other.x_shear
        self.y_shear = other.y_shear
        self.x_scale = other.x_scale
        self.y_scale = other.y_scale
        self.x_trapezoid = other.x_trapezoid
        self.y_trapezoid = other.y_trapezoid