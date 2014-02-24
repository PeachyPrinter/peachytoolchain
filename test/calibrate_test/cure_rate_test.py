import unittest
import sys
import os
from mock import patch, Mock
from testhelpers import TestHelpers

sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..', 'src', ))
from calibrate.cure_rate import CureRateCalibrator

class CureRateCalibrationTests(unittest.TestCase):
    sample_rate = 44100

    @patch('audio.drip_detector.DripDetector')
    def test_cure_rate_should_know_its_height_at_0(self, mock_DripDetector):
        mock_drip_detector =mock_DripDetector.return_value
        mock_drip_detector.num_drips = 0
        crc = CureRateCalibrator(mock_drip_detector, 10)

        self.assertEquals(crc.current_height_mm(),0)

    @patch('audio.drip_detector.DripDetector')
    def test_cure_rate_should_know_its_height_at_1000_drips(self, mock_DripDetector):
        mock_drip_detector = mock_DripDetector.return_value
        mock_drip_detector.num_drips = 1000
        drips_per_mm = 100
        crc = CureRateCalibrator(mock_drip_detector, drips_per_mm)

        self.assertEquals(crc.current_height_mm(),10)

    @patch('audio.drip_detector.DripDetector')
    def test_cure_rate_should_throw_an_exception_if_height_0_or_less(self, mock_DripDetector):
        mock_drip_detector = mock_DripDetector.return_value
        mock_drip_detector.num_drips = 1000
        drips_per_mm_fails = [-1.0,0,0.0]
        passed = True
        for drips_per_mm in drips_per_mm_fails:
            try:
                CureRateCalibrator(mock_drip_detector, drips_per_mm)
                passed = False
            except Exception as ex:
                pass
        self.assertTrue(passed)

    @patch('audio.drip_detector.DripDetector')
    def test_cure_rate_should_know_its_height_at_1000_drips(self, mock_DripDetector):
        mock_drip_detector = mock_DripDetector.return_value
        mock_drip_detector.num_drips = 1000
        drips_per_mm = 100
        crc = CureRateCalibrator(mock_drip_detector, drips_per_mm)

        self.assertEquals(crc.current_height_mm(),10)