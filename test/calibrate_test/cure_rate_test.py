import unittest
import sys
import os
from mock import patch, Mock
from testhelpers import TestHelpers
import time

sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..', 'src', ))
from calibrate.cure_rate import CureRateCalibrator

class CureRateCalibrationTests(unittest.TestCase):
    
    def test_CureRateCalibration_should_throw_exception_if_tuning_file_does_not_exist(self):
        passed = False
        try:
            CureRateCalibrator('nothere.dat')
            passed = False
        except:
            passed = True
        self.assertTrue(passed)

    def test_CureRateCalibration_should_throw_exception_if_tuning_file_invalid(self):
        passed = False
        try:
            CureRateCalibrator(os.path.join(os.path.dirname(__file__),'..','test_data','invalid.dat'))
            passed = False
        except:
            passed = True
        self.assertTrue(passed)

    def test_CureRateCalibration_should_load_valid_tuning_file(self):
        CureRateCalibrator(os.path.join(os.path.dirname(__file__),'..','test_data','valid.dat'))

