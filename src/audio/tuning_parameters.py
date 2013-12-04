class TuningParameters(object):
    build_x_min = -1.0
    build_x_max = 1.0
    build_y_min = -1.0
    build_y_max = 1.0
    x_offset = 0.0
    y_offset = 0.0
    rotation = 0.0
    x_shear = 0.0
    y_shear = 0.0
    x_scale = 1.0
    y_scale = 1.0
    x_trapezoid = 0.0
    y_trapezoid = 0.0

    def update(self, other):
        """Copy the values from another instance."""
        self.build_x_min = other.build_x_min
        self.build_x_max = other.build_x_max
        self.build_y_min = other.build_y_min
        self.build_y_max = other.build_y_max
        self.x_offset = other.x_offset
        self.y_offset = other.y_offset
        self.rotation = other.rotation
        self.x_shear = other.x_shear
        self.y_shear = other.y_shear
        self.x_scale = other.x_scale
        self.y_scale = other.y_scale
        self.x_trapezoid = other.x_trapezoid
        self.y_trapezoid = other.y_trapezoid
