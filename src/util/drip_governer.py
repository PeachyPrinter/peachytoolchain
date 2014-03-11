import serial
import time
import re

class DripGoverner(object):
    # _VALID_PORT = re.compile("COM[0-9]")
    connection = None
    def __init__(self, port):
        self.port = port
        self.connection = serial.Serial(self.port, 9600)

    def start_dripping(self):
        self.connection.write("1")

    def stop_dripping(self):
        self.connection.write("0")

    def close(self):
        self.connection.close()

    def __del__(self):
        self.close()
