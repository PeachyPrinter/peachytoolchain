
import unittest
import os
import sys
import StringIO

sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..','..', 'src', ))

from util.gcode_layer_mixer import GCodeLayerMixer




class GCodeLayerMixerTests(unittest.TestCase):
    test_file_path = os.path.join(os.path.dirname(__file__), '..', 'test_data')
    def test_reads_a_file_like_object(self):
        test_file = open(os.path.join(self.test_file_path, 'gcode.out'))
        
        mixer = GCodeLayerMixer(test_file)

    def test_should_not_move_Z_changes(self):
        test_data = "G1 Z1.0 F900.0\nG1 X0.00 Y0.00 F900.00\nM101\nG1 X1.00 Y1.00 F300.00 E1\nG1 Z2.0 F900.00\nG1 X0.01 Y0.01 F900.00\nM101\nG1 X1.01 Y1.01 F900.00 E1\n"

        expected1 = test_data.split('\n')[0]
        expected2 = test_data.split('\n')[4]
        
        actual = GCodeLayerMixer(StringIO.StringIO(test_data))
        actual_lines = list(actual)
        
        self.assertEqual(actual_lines[0],expected1)
        self.assertEqual(actual_lines[4],expected2)

    def test_should_cycle_between_Z_changes_if_one_layer(self):
        test_data= "G1 Z1.0 F900.0\nG1 X0.00 Y0.00 F900.00\nM101\nG1 X1.00 Y1.00 F300.00 E1"

        expected = "G1 Z1.0 F900.0\nM101\nG1 X1.00 Y1.00 F300.00 E1\nG1 X0.00 Y0.00 F900.00".split('\n')
        
        actual = GCodeLayerMixer(StringIO.StringIO(test_data))
        actual_lines = list(actual)
        
        self.assertEqual(actual_lines,expected, "\n%s\n%s" % (actual_lines,expected))
        
    def test_should_cycle_between_Z_changes_diffrently_for_each_layer(self):
        test_data= "G1 Z1.0 F900.0\nG1 X0.00 Y0.00 F900.00\nM101\nG1 X1.00 Y1.00 F300.00 E1\nG1 Z2.0 F900.00\nG1 X0.01 Y0.01 F900.00\nM101\nG1 X1.01 Y1.01 F900.00 E1\n"
        expected = "G1 Z1.0 F900.0\nM101\nG1 X1.00 Y1.00 F300.00 E1\nG1 X0.00 Y0.00 F900.00\nG1 Z2.0 F900.00\nG1 X1.01 Y1.01 F900.00 E1\nG1 X0.01 Y0.01 F900.00\nM101".split('\n')
        actual = GCodeLayerMixer(StringIO.StringIO(test_data))
        actual_lines = list(actual)
        
        self.assertEqual(actual_lines,expected,"\n%s\n%s" % (actual_lines,expected))

# Laser on/off
# Looks for rapid 
# One Item Lists

if __name__ == '__main__':
    unittest.main()