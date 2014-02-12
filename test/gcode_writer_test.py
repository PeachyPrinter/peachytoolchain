import unittest
import tempfile
import shutil
import os
import sys

sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..', 'src'))
from gcode_writer import GcodeWriter, MoveModes


test_data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_data')
def dataFile(filename):
    return os.path.join(test_data_path, filename)


class GcodeWriterTest(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix='unittest')

    def tearDown(self):
        if self.tmp_dir is not None:
            if True:
                shutil.rmtree(self.tmp_dir)
            else:
                print('*** Leaving temp files in directory "%s"' % self.tmp_dir)

    def test(self):
        filepath = os.path.join(self.tmp_dir, 'gcode.out')
        with open(filepath, 'wt') as outfile:
            writer = GcodeWriter(outfile, 300.0, 900.0)
            writer.moveToHeight(0.01)
            writer.drawPath([(0.0, 0.0), (1.0, 1.0), (1.0, -1.0), (-1.0, 1.0), (-1.0, -1.0), (0.0, 0.0)])
            writer.moveToHeight(0.02)
            writer.drawPath([(0.0, 0.0), (1.0, 1.0), (1.0, -1.0), (-1.0, 1.0), (-1.0, -1.0), (0.0, 0.0)])
            writer.moveToHeight(0.03)
            writer.drawPath([(-1.0, 1.0), (1.0, 1.0), (1.0, -1.0), (-1.0, -1.0)])
            writer.moveToHeight(0.04)
            writer.drawPath([(0.0, 0.0), (1.0, 1.0), (1.0, -1.0), (-1.0, 1.0), (-1.0, -1.0), (0.0, 0.0)])
        self.assertEqual(open(dataFile('gcode.out')).read(), open(filepath,'rt').read())
        

if __name__ == '__main__':
    unittest.main()