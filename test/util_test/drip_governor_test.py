import unittest
import sys
import os
import time
from mock import patch

sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..','..', 'src', ))

from util.drip_governor import DripGovernor

class DripGovernorTests(unittest.TestCase):

    @patch('serial.Serial')
    def test_should_create_a_connection(self, mock_Serial):       
        drip_governor = DripGovernor('COM4')

        self.assertTrue(mock_Serial.call_args[0] == ('COM4',9600))

    @patch('serial.Serial')
    def test_should_close_the_connection(self, mock_Serial):
        drip_governor = DripGovernor('COM4')
        my_mock_serial = mock_Serial.return_value

        drip_governor.close()

        my_mock_serial.close.assert_called_with()

    @patch('serial.Serial')
    def test_should_write_1_when_on(self, mock_Serial):
        drip_governor = DripGovernor('COM4')
        my_mock_serial = mock_Serial.return_value

        drip_governor.start_dripping()

        my_mock_serial.write.assert_called_with("1")

    @patch('serial.Serial')
    def test_should_write_0_when_off(self, mock_Serial):
        drip_governor = DripGovernor('COM4')
        my_mock_serial = mock_Serial.return_value
        drip_governor.start_dripping()

        drip_governor.stop_dripping()

        my_mock_serial.write.assert_called_with("0")

    @patch('serial.Serial')
    def test_should_not_write_a_1_when_already_on(self, mock_Serial):
        drip_governor = DripGovernor('COM4')
        my_mock_serial = mock_Serial.return_value
        drip_governor.start_dripping()
        self.assertEqual(1, my_mock_serial.write.call_count, "Setup failed")

        drip_governor.start_dripping()
        
        self.assertEqual(1, my_mock_serial.write.call_count)

    @patch('serial.Serial')
    def test_should_not_write_a_0_when_already_off(self, mock_Serial):
        drip_governor = DripGovernor('COM4')
        my_mock_serial = mock_Serial.return_value
        drip_governor.stop_dripping()
        self.assertEqual(1, my_mock_serial.write.call_count, "Setup failed")

        drip_governor.stop_dripping()
        
        self.assertEqual(1, my_mock_serial.write.call_count)

    @patch('serial.Serial')
    def test_should_write_a_0_when_already_on_and_off_requested(self, mock_Serial):
        drip_governor = DripGovernor('COM4')
        my_mock_serial = mock_Serial.return_value
        drip_governor.start_dripping()
        self.assertEqual(1, my_mock_serial.write.call_count, "Setup failed")

        drip_governor.stop_dripping()
        
        my_mock_serial.write.assert_called_with("0")


    @patch('serial.Serial')
    def test_should_write_a_1_when_already_off_and_on_requested(self, mock_Serial):
        drip_governor = DripGovernor('COM4')
        my_mock_serial = mock_Serial.return_value
        drip_governor.stop_dripping()

        drip_governor.start_dripping()
        
        my_mock_serial.write.assert_called_with("1")

    @patch('serial.Serial')
    def test_should_be_able_to_toggle_on_and_off(self, mock_Serial):
        drip_governor = DripGovernor('COM4')
        my_mock_serial = mock_Serial.return_value
        drip_governor.start_dripping()
        drip_governor.stop_dripping()

        drip_governor.start_dripping()

        my_mock_serial.write.assert_called_with("1")

    @patch('serial.Serial')
    def test_should_be_able_to_toggle_off_and_on(self, mock_Serial):
        drip_governor = DripGovernor('COM4')
        my_mock_serial = mock_Serial.return_value
        drip_governor.stop_dripping()
        drip_governor.start_dripping()

        drip_governor.stop_dripping()

        my_mock_serial.write.assert_called_with("0")

    @patch('serial.Serial')
    def test_should_call_on_periodically(self, mock_Serial):
        drip_governor = DripGovernor('COM4', 10)
        my_mock_serial = mock_Serial.return_value

        drip_governor.start_dripping()
        time.sleep(0.011)
        drip_governor.start_dripping()

        self.assertEqual(2, my_mock_serial.write.call_count)

    @patch('serial.Serial')
    def test_should_call_off_periodically(self, mock_Serial):
        drip_governor = DripGovernor('COM4', 10)
        my_mock_serial = mock_Serial.return_value

        drip_governor.stop_dripping()
        time.sleep(0.011)
        drip_governor.stop_dripping()

        self.assertEqual(2, my_mock_serial.write.call_count)


if __name__ == '__main__':
    unittest.main()