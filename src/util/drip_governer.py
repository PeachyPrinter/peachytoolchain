import serial
import time
import re

class DripGoverner(object):
    _connection = None
    _flow_on = False
    _last_update = 0

    def _current_milli_time(self):
        return int(round(time.time() * 1000))

    def __init__(self, port, repeat_delay_ms = 2000):
        self._port = port
        self._repeat_delay_ms = repeat_delay_ms
        self._connection = serial.Serial(self._port, 9600)
        self._last_update = self._current_milli_time()

    def _old(self):
        return self._current_milli_time() - self._last_update > self._repeat_delay_ms


    def start_dripping(self):
        if self._flow_on == False or self._old():
            self._last_update = self._current_milli_time()
            self._connection.write('1')
            self._flow_on = True

    def stop_dripping(self):
        if self._flow_on == True or self._old():
            self._last_update = self._current_milli_time()
            self._connection.write('0')
            self._flow_on = False

    def close(self):
        self._connection.close()

    def __del__(self):
        self.close()
