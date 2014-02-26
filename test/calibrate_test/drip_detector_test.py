import unittest
import sys
import os
from mock import patch, Mock
from testhelpers import TestHelpers
import wave
import pyaudio 
import time

sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..', 'src', ))
from calibrate.drip_detector import DripDetector

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
    time_to_wait = 0.3
    stream = None

    def tearDown(self):
        try:
            self.stream.close()
        except:
            pass

    def test_drip_detector_should_report_height_of_0_when_stopped(self):
        drips_per = 1
        drip_detector = DripDetector(drips_per)
        self.assertEqual(drip_detector.get_height_mm(), 0)

    @patch('pyaudio.PyAudio')
    def test_drip_detector_should_report_1_drips_after_1_slow_drips(self, mock_pyaudio):
        drips_per = 1
        wave_file = os.path.join(self.test_file_path, '1_drip.wav')
        self.stream = MockPyAudioStream(wave_file)

        my_mock_pyaudio = mock_pyaudio.return_value
        my_mock_pyaudio.open.return_value = self.stream

        drip_detector = DripDetector(drips_per)
        drip_detector.start()
        time.sleep(self.time_to_wait)
        drip_detector.stop()
        self.assertEqual(drip_detector.get_height_mm(), 1)

    @patch('pyaudio.PyAudio')
    def test_drip_detector_should_not_round_up_drips(self, mock_pyaudio):
        drips_per = 10
        wave_file = os.path.join(self.test_file_path, '1_drip.wav')
        self.stream = MockPyAudioStream(wave_file)

        my_mock_pyaudio = mock_pyaudio.return_value
        my_mock_pyaudio.open.return_value = self.stream

        drip_detector = DripDetector(drips_per)
        drip_detector.start()
        time.sleep(self.time_to_wait)
        drip_detector.stop()
        self.assertEqual(drip_detector.get_height_mm(), 0.1)

    @patch('pyaudio.PyAudio')
    def test_drip_detector_should_report_1_drips_after_1_fast_drips(self, mock_pyaudio):
        drips_per = 1
        wave_file = os.path.join(self.test_file_path, '1_drip_fast.wav')
        self.stream = MockPyAudioStream(wave_file)

        my_mock_pyaudio = mock_pyaudio.return_value
        my_mock_pyaudio.open.return_value = self.stream

        drip_detector = DripDetector(drips_per)
        drip_detector.start()
        time.sleep(self.time_to_wait)
        drip_detector.stop()
        self.assertEqual(drip_detector.get_height_mm(), 1)

    @patch('pyaudio.PyAudio')
    def test_drip_detector_should_report_14_drips_after_14_drips(self, mock_pyaudio):
        drips_per = 1
        wave_file = os.path.join(self.test_file_path, '14_drips.wav')
        self.stream = MockPyAudioStream(wave_file)

        my_mock_pyaudio = mock_pyaudio.return_value
        my_mock_pyaudio.open.return_value = self.stream

        drip_detector = DripDetector(drips_per)
        drip_detector.start()
        time.sleep(self.time_to_wait)
        drip_detector.stop()
        self.assertEqual(drip_detector.get_height_mm(), 14)

    @patch('pyaudio.PyAudio')
    def test_drip_detector_should_report_22_drips_after_22_drips_speed_up(self, mock_pyaudio):
        drips_per = 1
        wave_file = os.path.join(self.test_file_path, '22_drips_speeding_up.wav')
        self.stream = MockPyAudioStream(wave_file)

        my_mock_pyaudio = mock_pyaudio.return_value
        my_mock_pyaudio.open.return_value = self.stream

        drip_detector = DripDetector(drips_per)
        drip_detector.start()
        time.sleep(self.time_to_wait)
        drip_detector.stop()
        self.assertEqual(drip_detector.get_height_mm(), 22)

    @patch('pyaudio.PyAudio')
    def test_drip_detector_should_run_in_its_own_thread(self, mock_pyaudio):
        drips_per = 1
        wave_file = os.path.join(self.test_file_path, '22_drips_speeding_up.wav')
        self.stream = MockPyAudioStream(wave_file)

        my_mock_pyaudio = mock_pyaudio.return_value
        my_mock_pyaudio.open.return_value = self.stream

        drip_detector = DripDetector(drips_per)
        drip_detector.start()
        drip_detector.stop()
        self.assertTrue(drip_detector.get_height_mm() < 22)

    @patch('pyaudio.PyAudio')
    def test_drip_detector_should_report_2_drips_if_started_half_way_though_drip(self, mock_pyaudio):
        drips_per = 1
        wave_file = os.path.join(self.test_file_path, 'half_and_1_drips.wav')
        self.stream = MockPyAudioStream(wave_file)

        my_mock_pyaudio = mock_pyaudio.return_value
        my_mock_pyaudio.open.return_value = self.stream

        drip_detector = DripDetector(drips_per)
        drip_detector.start()
        time.sleep(self.time_to_wait)
        drip_detector.stop()
        self.assertEqual(drip_detector.get_height_mm(), 2)
