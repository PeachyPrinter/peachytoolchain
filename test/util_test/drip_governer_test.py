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

    # @patch('serial.Serial')
    # def test_should_create_a_connection(self, mock_Serial):
    #     my_mock_Serial = mock_Serial.return_value
        
    #     drip_governer = DripGoverner('COM4')


if __name__ == '__main__':
    unittest.main()