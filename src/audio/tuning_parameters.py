class TuningParameters(object):
    x_offset = 0.0
    y_offset = 0.0
    rotation = 0.0
    x_shear = 0.0
    y_shear = 0.0
    x_scale = 1.0
    y_scale = 1.0
    x_trapezoid = 0.0
    y_trapezoid = 0.0
    x_pin_radius = 20.0
    x_pin_phase = 0.0
    y_pin_radius = 20.0
    y_pin_phase = 0.0

    def update(self, other):
        """Copy the values from another instance."""
        self.x_offset = other.x_offset
        self.y_offset = other.y_offset
        self.rotation = other.rotation
        self.x_shear = other.x_shear
        self.y_shear = other.y_shear
        self.x_scale = other.x_scale
        self.y_scale = other.y_scale
        self.x_trapezoid = other.x_trapezoid
        self.y_trapezoid = other.y_trapezoid
        self.x_pin_radius = other.x_pin_radius
        self.x_pin_phase = other.x_pin_phase
        self.y_pin_radius = other.y_pin_radius
        self.y_pin_phase = other.y_pin_phase
