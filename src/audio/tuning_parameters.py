class TuningParameters(object):
    x_offset = 0.0
    y_offset = 0.0
    rotation = 0.0
    x_shear = 0.0
    y_shear = 0.0
    x_scale = 1.0
    y_scale = 1.0

    def update(self, other):
        """Copy the values from another instance."""
        self.x_offset = other.x_offset
        self.y_offset = other.y_offset
        self.rotation = other.rotation
        self.x_shear = other.x_shear
        self.y_shear = other.y_shear
        self.x_scale = other.x_scale
        self.y_scale = other.y_scale
