import unittest
import sys
import os
from mock import patch

sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..','..', 'src', ))

from util.drip_governer import DripGoverner

class DripGovernerTests(unittest.TestCase):

    @patch('serial.Serial')
    def test_should_require_a_valid_com_port(self, mock_Serial):
        passed = False
        try:
            DripGoverner('bla12')
            passed = False
        except:
            passed = True
        self.assertTrue(passed)

    @patch('serial.Serial')
    def test_should_create_a_connection(self, mock_Serial):       
        drip_governer = DripGoverner('COM4')

        self.assertTrue(mock_Serial.call_args[0] == ('COM4',9600))

    @patch('serial.Serial')
    def test_should_close_the_connection(self, mock_Serial):
        drip_governer = DripGoverner('COM4')
        my_mock_serial = mock_Serial.return_value
        drip_governer.close()
        my_mock_serial.close.assert_called_with()

    @patch('serial.Serial')
    def test_should_write_1_when_on(self, mock_Serial):
        drip_governer = DripGoverner('COM4')
        my_mock_serial = mock_Serial.return_value
        drip_governer.start_dripping()
        my_mock_serial.write.assert_called_with("1")

    @patch('serial.Serial')
    def test_should_write_0_when_off(self, mock_Serial):
        drip_governer = DripGoverner('COM4')
        my_mock_serial = mock_Serial.return_value
        drip_governer.stop_dripping()
        my_mock_serial.write.assert_called_with("0")

if __name__ == '__main__':
    unittest.main()