import unittest
import sys
import os
from mock import patch, Mock
from testhelpers import TestHelpers
import wave
import pyaudio 
import time

sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..', 'src', ))
from calibrate.cure_rate import CureRateCalibrator, DripDetector

class MockPyAudioStream(object):
    _read_frames = 0
    def __init__(self, wavefile, chunk_size = 1024):
        self._wave_data = wave.open(wavefile, 'rb')
        self._chunk_size = chunk_size
    
    def read(self,frames):
        self._read_frames += frames
        return self._wave_data.readframes(frames)
    def get_read_available(self):
        possible_frames = self._wave_data.getnframes() - self._read_frames
        if (possible_frames >= self._chunk_size):
            return self._chunk_size
        else:
            return possible_frames
    def start_stream(self):
        pass
    def stop_stream(self):
        pass
    def close(self):
        self._wave_data.close()


class DripDetectorTests(unittest.TestCase):
    test_file_path = os.path.join(os.path.dirname(__file__), '..', 'test_data')
    p = pyaudio.PyAudio()

    def test_drip_detector_should_report_height_of_0_when_stopped(self):
        drips_per = 1
        drip_detector = DripDetector(1)
        self.assertEqual(drip_detector.get_height_mm(), 0)

    @patch('pyaudio.PyAudio')
    def test_drip_detector_should_report_1_drips_after_1_slow_drips(self, mock_pyaudio):
        drips_per = 1
        wave_file = os.path.join(self.test_file_path, '1_drip.wav')
        stream = MockPyAudioStream(wave_file)

        my_mock_pyaudio = mock_pyaudio.return_value
        my_mock_pyaudio.open.return_value = stream

        drip_detector = DripDetector(1)
        drip_detector.start()
        time.sleep(1)
        drip_detector.stop()
        self.assertEqual(drip_detector.get_height_mm(), 1)

    @patch('pyaudio.PyAudio')
    def test_drip_detector_should_report_1_drips_after_1_fast_drips(self, mock_pyaudio):
        drips_per = 1
        wave_file = os.path.join(self.test_file_path, '1_drip_fast.wav')
        stream = MockPyAudioStream(wave_file)

        my_mock_pyaudio = mock_pyaudio.return_value
        my_mock_pyaudio.open.return_value = stream

        drip_detector = DripDetector(1)
        drip_detector.start()
        time.sleep(1)
        drip_detector.stop()
        self.assertEqual(drip_detector.get_height_mm(), 1)

    @patch('pyaudio.PyAudio')
    def test_drip_detector_should_report_14_drips_after_14_drips(self, mock_pyaudio):
        drips_per = 1
        wave_file = os.path.join(self.test_file_path, '14_drips.wav')
        stream = MockPyAudioStream(wave_file)

        my_mock_pyaudio = mock_pyaudio.return_value
        my_mock_pyaudio.open.return_value = stream

        drip_detector = DripDetector(1)
        drip_detector.start()
        time.sleep(1)
        drip_detector.stop()
        self.assertEqual(drip_detector.get_height_mm(), 14)

    @patch('pyaudio.PyAudio')
    def test_drip_detector_should_report_22_drips_after_22_drips_speed_up(self, mock_pyaudio):
        drips_per = 1
        wave_file = os.path.join(self.test_file_path, '22_drips_speeding_up.wav')
        stream = MockPyAudioStream(wave_file)

        my_mock_pyaudio = mock_pyaudio.return_value
        my_mock_pyaudio.open.return_value = stream

        drip_detector = DripDetector(1)
        drip_detector.start()
        time.sleep(1)
        drip_detector.stop()
        self.assertEqual(drip_detector.get_height_mm(), 22)

    #start half way through

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
    def test_cure_rate_should_send_audio_test_pattern(self, mock_DripDetector):
        mock_drip_detector = mock_DripDetector.return_value
        mock_drip_detector.num_drips = 1000
        drips_per_mm = 100
        crc = CureRateCalibrator(mock_drip_detector, drips_per_mm, )

        self.assertEquals(crc.current_height_mm(),10)
