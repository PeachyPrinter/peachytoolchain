import serial
import time
import re

class DripGoverner(object):
    _VALID_PORT = re.compile("COM[0-9]")
    def __init__(self, port):
        if _VALID_PORT.match(port):
            self.port = port
        else:
            raise ('%s is not a valid port try should be in the format "COM2"')

    def start_dripping(self):
        pass

    def stop_dripping(self):
        pass