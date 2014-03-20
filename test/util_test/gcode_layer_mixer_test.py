
import unittest
import os

from util.gcode_layer_mixer import GCodeLayerMixer

class GCodeLayerMixerTests(unittest.TestCase):
    test_file_path = os.path.join(os.path.dirname(__file__), '..', 'test_data')

    def test_reads_a_file_like_object(self):
        test_file = open(os.path.join(self.test_file_path, 'gcode.out'))
        mixer = GCodeLayerMixer()
        mixer.mix(test_file)
