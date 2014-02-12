import unittest
import os

import gcode_writer_test
import calibrate

loader = unittest.TestLoader()
suite = loader.discover(os.path.dirname(__file__), pattern='*test.py')

runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)

exit(len(result.errors) + len(result.failures))