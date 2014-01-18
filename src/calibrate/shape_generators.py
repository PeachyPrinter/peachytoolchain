import threading
import math

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
        return [self.center]*n

class SquareGenerator(object):
    def __init__(self, sampling_rate, speed, size, center):
        """
        Generator that creates a square with bounds +/- [-1.0, 1.0], drawing at a speed of 'speed' units per second.
        Note that for a square within the range [-1.0, 1.0], the total circumference is 8 units, so it will take
        8 seconds to complete the shape when drawing at 1 unit per second.

        sampling_rate -- int -- The number of points per second to draw (should match the audio sampling rate)
        speed -- float -- The speed at which to follow the object path in units per second.
        size -- float -- The size in "units" to draw the square. It will be this many units on-side. (+/- 0.5 size)
        center -- (x, y) -- The coordinates where the center of the shape should be drawn.
        """
        self.cycle = 0
        self._sampling_rate = int(sampling_rate)
        self._speed = float(speed)
        self._size = float(size)
        self.center = center
        self._lock = threading.Lock()
        self._update_cycles()

        self._side_directions = [(+1, 0), (0, -1), (-1, 0), (0, +1)] # (top, right, bottom, left)
        self._side_constants = [(0, +1), (+1, 0), (0, -1), (-1, 0)] # (top, right, bottom, left)

    def _getXY(self, cycle):
        current_side = self.cycle // self._cycles_per_side
        side_cycle = self.cycle % self._cycles_per_side
        side_fraction = -1.0 + 2.0*(float(side_cycle) / float(self._cycles_per_side)) # range [-1, 1)
        side_constant = self._side_constants[current_side]
        side_direction = self._side_directions[current_side]
        side_x = (self._size/2.0)*(float(side_constant[0]) + side_fraction*float(side_direction[0])) + self.center[0]
        side_y = (self._size/2.0)*(float(side_constant[1]) + side_fraction*float(side_direction[1])) + self.center[1]
        return side_x, side_y

    def nextN(self, n):
        """Returns the next N points as a list of (x, y) tuples."""
        with self._lock:
            values = []
            count = 0
            while count < n:
                values.append(self._getXY(self.cycle))
                count += 1
                self.cycle += 1
                if self.cycle >= self._total_cycles:
                    self.cycle = 0
            return values

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
        self._cycles_per_side = int(2.0*self._size*float(self.sampling_rate)/self._speed)
        self._total_cycles = self._cycles_per_side * 4
        self.cycle = 0


class StarGenerator(object):
    def __init__(self, sampling_rate, speed, size, center):
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

        sampling_rate -- int -- The number of points per second to draw (should match the audio sampling rate)
        speed -- float -- The speed at which to follow the object path in units per second.
        size -- float -- The size in "units" to draw the star. It will be this large on-side (+/- 0.5 size)
        center -- (x, y) -- The coordinates where the center of the shape should be drawn.
        """
        self._vertices = [(0.0, 0.0), (0.3, 0.0), (0.4, 0.1), (0.5, 0.0), (0.6, -0.1), (0.7, 0.0), (1.0, 0.0),
                          (0.0, 1.0), (0.0, 0.7), (-0.1, 0.6), (0.0, 0.5), (0.1, 0.4), (0.0, 0.3),
                          (0.0, 0.0), (-0.3, 0.0), (-0.4, -0.1), (-0.5, 0.0), (-0.6, 0.1), (-0.7, 0.0), (-1.0, 0.0),
                          (0.0, -1.0), (0.0, -0.7), (0.1, -0.6), (0.0, -0.5), (-0.1, -0.4), (0.0, -0.3),
                        ]
        self.cycle = 0
        self._sampling_rate = int(sampling_rate)
        self._speed = speed
        self._size = size
        self.center = center
        self._lock = threading.Lock()
        self._update_cycles()

    @property
    def sampling_rate(self):
        return self._sampling_rate

    @sampling_rate.setter
    def sampling_rate(self, rate):
        with self._lock:
            self.sampling_rate = rate
            self._update_cycles()

    @property
    def speed(self, speed):
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

    def _calculate_path_length(self, vertices):
        length = 0.0
        last_vert = vertices[0]
        for next_vert in vertices[1:]:
            length += math.sqrt(
                    math.pow(next_vert[0] - last_vert[0], 2.0) +
                    math.pow(next_vert[1] - last_vert[1], 2.0)
            )
            last_vert = next_vert
        return length

    def _update_cycles(self):
        self._cycle_step = self._speed/float(self._sampling_rate)
        self.cycle = 0
        self._current_segment_start = 0
        self._current_segment_dist_taken = 0.0

    def nextN(self, N):
        """Returns the next N points as a list of (x, y) tuples."""
        with self._lock:
            values = []
            for n in range(N):
                values.append(self._next())
            return values

    def _next(self):
        while True:
            # Keep iterating through segments until we reach the next point (should normally only loop once, if at all)
            current_vert = self._get_vertices(self._current_segment_start)
            next_vert = self._get_vertices((self._current_segment_start + 1) % len(self._vertices))
            current_segment_length = self._calculate_path_length([current_vert, next_vert])
            self._current_segment_dist_taken = self._current_segment_dist_taken + self._cycle_step
            if self._current_segment_dist_taken < current_segment_length:
                break
            # Use only part of the path length on this segment then start on the next segment
            self._current_segment_dist_taken -= current_segment_length
            self._current_segment_start = (self._current_segment_start + 1) % len(self._vertices)
        # Find the current point in this segment
        x = current_vert[0] + (self._current_segment_dist_taken/current_segment_length)*(next_vert[0] - current_vert[0])
        y = current_vert[1] + (self._current_segment_dist_taken/current_segment_length)*(next_vert[1] - current_vert[1])
        return (x, y)

    def _get_vertices(self, index):
        """Returns the vertices at the given index, scaled by the current size."""
        norm_vert = self._vertices[index]
        scaled_vert = ((self._size/2.0)*norm_vert[0]+self.center[0], (self._size/2.0)*norm_vert[1]+self.center[1])
        return scaled_vert
