import threading
import math

class NullGenerator(object):
    def nextN(self, n):
        return [(0.0, 0.0)]*n
    def set_wave_rate(self, rate):
        pass
    def set_speed(self, speed):
        pass

class SquareGenerator(object):
    def __init__(self, wave_rate=8000, speed=1.0):
        """Creates a square with bounds +/- size (in [-1.0, 1.0] range),drawing freq times
        per second.
        """
        print('created square gen')
        self.cycle = 0
        self.wave_rate = int(wave_rate)
        self.freq = speed

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
        side_x = float(side_constant[0]) + side_fraction*float(side_direction[0])
        side_y = float(side_constant[1]) + side_fraction*float(side_direction[1])
        return side_x, side_y

    def nextN(self, n):
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

    def set_wave_rate(self, wave_rate):
        with self._lock:
            self.wave_rate = wave_rate
            self._update_cycles()

    def set_speed(self, speed):
        with self._lock:
            self.freq = speed
            self._update_cycles()

    def _update_cycles(self):
        self._cycles_per_side = int(float(self.wave_rate)/(4.0*self.freq))
        self._total_cycles = self._cycles_per_side * 4
        self.cycle = 0


class StarGenerator(object):
    def __init__(self, wave_rate=8000, speed=1.0):
        self._vertices = [(0.0, 0.0), (0.3, 0.0), (0.4, 0.1), (0.5, 0.0), (0.6, -0.1), (0.7, 0.0), (1.0, 0.0),
                          (0.0, 1.0), (0.0, 0.7), (-0.1, 0.6), (0.0, 0.5), (0.1, 0.4), (0.0, 0.3),
                          (0.0, 0.0), (-0.3, 0.0), (-0.4, -0.1), (-0.5, 0.0), (-0.6, 0.1), (-0.7, 0.0), (-1.0, 0.0),
                          (0.0, -1.0), (0.0, -0.7), (0.1, -0.6), (0.0, -0.5), (-0.1, -0.4), (0.0, -0.3),
                        ]
        self._total_length = self._calculate_path_length(self._vertices)

        self.cycle = 0
        self.wave_rate = int(wave_rate)
        self.freq = speed

        self._lock = threading.Lock()

        self._update_cycles()

    def set_wave_rate(self, wave_rate):
        with self._lock:
            self.wave_rate = wave_rate
            self._update_cycles()

    def set_speed(self, speed):
        with self._lock:
            self.freq = speed
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
        self._total_cycles = int(self.wave_rate/self.freq)
        self._cycle_step = self._total_length/float(self._total_cycles)
        self._current_segment_start = 0
        self._current_segment_dist_taken = 0.0

    def nextN(self, N):
        values = []
        for n in range(N):
            values.append(self._next())
        return values

    def _next(self):
        while True:
            # Keep iterating through segments until we reach the next point (should normally only loop once, if at all)
            current_vert = self._vertices[self._current_segment_start]
            next_vert = self._vertices[(self._current_segment_start + 1) % len(self._vertices)]
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