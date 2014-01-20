import threading
import math
import numpy


class NullGenerator(object):
    def __init__(self, sampling_rate, speed, size, center):
        """
        Generator that always returns coordinates from the center position..
        """
        self.sampling_rate = int(sampling_rate)
        self.speed = float(speed)
        self.size = float(size)
        self.center = center

    def nextN(self, n):
        """Returns the next N points as a list of (x, y) tuples."""
        x_array = numpy.ones((n, 1)) * self.center[0]
        y_array = numpy.ones((n, 1)) * self.center[1]
        return numpy.column_stack((x_array, y_array))


class PathGenerator(object):
    """
    Superclass for generators that follow a defined path in normalized space.
    This class implements all the logic needed to follow the path. To use it, subclass it and override
    the class attribute PATH with a list of (x,y) vertices that define the closed path.
    """
    PATH = None
    def __init__(self, sampling_rate, speed, size, center):
        """
        sampling_rate -- int -- The number of points per second to draw (should match the audio sampling rate)
        speed -- float -- The speed at which to follow the object path in units per second.
        size -- float -- The size in "units" to draw the shape. It will be this large on-side (+/- 0.5 size)
        center -- (x, y) -- The coordinates where the center of the shape should be drawn.
        """
        self._sampling_rate = int(sampling_rate)
        self._speed = speed
        self._size = size
        self.center = center
        self._lock = threading.Lock()
        self._update_cycles()
        self._current_position = tuple(self.center)
        self._next_vertex_index = 0

    @property
    def sampling_rate(self):
        return self._sampling_rate

    @sampling_rate.setter
    def sampling_rate(self, rate):
        with self._lock:
            self.sampling_rate = rate
            self._update_cycles()

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, speed):
        with self._lock:
            self._speed = speed
            self._update_cycles()

    @property
    def size(self):
        with self._lock:
            return self._size

    @size.setter
    def size(self, size):
        with self._lock:
            self._size = size
            self._update_cycles()

    def _update_cycles(self):
        self._cycle_step = self._speed/float(self._sampling_rate)

    def nextN(self, n):
        """Returns the next 'n' samples of the shape."""
        samples = numpy.empty((n, 2))
        n_left = n
        while n_left:
            # Figure out how far until the next vertex
            cur_x, cur_y = self._current_position
            next_x, next_y = self._get_vertex(self._next_vertex_index)
            distance = math.sqrt(
                math.pow(next_x - cur_x, 2.0)
                + math.pow(next_y - cur_y, 2.0)
            )
            # Edge case: just in case we some how end "on" the next vertex; advance to the next vertex immediately
            if distance == 0.0:
                self._next_vertex_index = (self._next_vertex_index + 1) % len(self.PATH)
                continue
            num_samples_needed = distance / self._cycle_step
            # Do we have enough samples left to hit the end?
            if num_samples_needed > n_left:
                # Not enough samples, so go as far as we can
                num_samples = n_left
                cosine_x = (next_x - self._current_position[0]) / distance
                cosine_y = (next_y - self._current_position[1]) / distance
                end_x = cur_x + cosine_x * self._cycle_step * num_samples
                end_y = cur_y + cosine_y * self._cycle_step * num_samples
            else:
                # At least enough, so use as many as needed to get there and advance to next vertex
                num_samples = int(math.ceil(num_samples_needed))
                end_x = next_x
                end_y = next_y
                self._next_vertex_index = (self._next_vertex_index + 1) % len(self.PATH)
            # NOTE: Have to manually compute positive indices because using negative indices can lead to 0 as an end
            start_i = n-n_left
            end_i = start_i+num_samples
            samples[start_i:end_i,0] = numpy.linspace(cur_x, end_x, num=num_samples, endpoint=False)
            samples[start_i:end_i,1] = numpy.linspace(cur_y, end_y, num=num_samples, endpoint=False)
            n_left -= num_samples
            self._current_position = (end_x, end_y)
        return samples

    def _get_vertex(self, index):
        """Returns the vertex at the given index, scaled by the current size."""
        norm_vert = self.PATH[index]
        scaled_vert = ((self._size/2.0)*norm_vert[0]+self.center[0], (self._size/2.0)*norm_vert[1]+self.center[1])
        return scaled_vert


class StarGenerator(PathGenerator):
    """
    Generator that creates a star-like pattern with bounds +/- [-1.0, 1.0] range, drawing at a speed of 'speed'
    units per second.

    This shape, which looks kind of like an hour glass rotated 45 degrees, can be used to determine:
     * Scale (extents of the points should be +/- 1.0)
     * Rotation (draws horizontal and vertical lines)
     * Offset (vertical and horizontal lines should meet at (0.0, 0.0))
     * Memory/hysteresis (without memory, top-left and bottom-right angles should meet exactly in the center,
       memory will cause them to be separated)
     * Linearity (sides should be 45 degree angles; ticks along the axes should all be equally spaced)
     * Maximum speed (if moving too fast, sharp angles will be rounded; if ringing, long lines will be wavy)
    """
    PATH =  [(0.0, 0.0), (0.3, 0.0), (0.4, 0.1), (0.5, 0.0), (0.6, -0.1), (0.7, 0.0), (1.0, 0.0),
                         (0.0, 1.0), (0.0, 0.7), (-0.1, 0.6), (0.0, 0.5), (0.1, 0.4), (0.0, 0.3),
                         (0.0, 0.0), (-0.3, 0.0), (-0.4, -0.1), (-0.5, 0.0), (-0.6, 0.1), (-0.7, 0.0), (-1.0, 0.0),
                         (0.0, -1.0), (0.0, -0.7), (0.1, -0.6), (0.0, -0.5), (-0.1, -0.4), (0.0, -0.3)]


class SquareGenerator(PathGenerator):
    """
    Generator that creates a simple square. Useful for testing transformations during calibration.
    """
    PATH =  [(-1.0, -1.0), (1.0, -1.0), (1.0, 1.0), (-1.0, 1.0)]
