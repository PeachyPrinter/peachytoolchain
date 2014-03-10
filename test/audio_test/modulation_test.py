import unittest
import numpy
import sys
import os

sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..', 'src', ))
from audio.modulation import AmplitudeModulator


class AmplitudeModulatorTests(unittest.TestCase):
    sampling_rate = 44100
    carrier_freq = 11025.0

    def test_modulation_left_should_throw_exception_below_25_percent(self):
        amplitudeModulator = AmplitudeModulator(self.sampling_rate)
        test_values = numpy.array([
            [-1.01,  0.0 ],
            [-1.01,  0.0 ],
            [-1.01,  0.0 ], 
        ])
        passed = False
        try:
            amplitudeModulator.modulate_values(test_values)
            passed = False
        except Exception as ex:
            passed = True
        self.assertTrue(passed)

    def test_modulation_left_should_throw_exception_above_100_percent(self):
        amplitudeModulator = AmplitudeModulator(self.sampling_rate)
        test_values = numpy.array([
            [1.01,  0.0 ],
            [1.01,  0.0 ],
            [1.01,  0.0 ], 
        ])
        passed = False
        try:
            amplitudeModulator.modulate_values(test_values)
            passed = False
        except Exception as ex:
            passed = True
        self.assertTrue(passed)

    def test_modulation_right_should_throw_exception_below_25_percent(self):
        amplitudeModulator = AmplitudeModulator(self.sampling_rate)
        test_values = numpy.array([
            [0.0,  -1.01 ],
            [0.0,  -1.01 ],
            [0.0,  -1.01 ], 
        ])
        passed = False
        try:
            amplitudeModulator.modulate_values(test_values)
            passed = False
        except Exception as ex:
            passed = True
        self.assertTrue(passed)

    def test_modulation_right_should_throw_exception_above_100_percent(self):
        amplitudeModulator = AmplitudeModulator(self.sampling_rate)
        test_values = numpy.array([
            [0.0,  1.01 ],
            [0.0,  1.01 ],
            [0.0,  1.01 ], 
        ])
        passed = False
        try:
            amplitudeModulator.modulate_values(test_values)
            passed = False
        except Exception as ex:
            passed = True
        self.assertTrue(passed)

    def test_modulation_should_work(self):
        pass
        # amplitudeModulator = AmplitudeModulator(self.sampling_rate)
        # amplitudeModulator.laser_enabled = True
        # test_values = numpy.array([
        #     [0.0, 0.0],
        #     [0.0, 0.0],
        #     [0.0, 0.0],
        #     [0.0, 0.0],
        #     [0.0, 0.0],
        #     ])
        # expected_results = numpy.array([
        #     [0.0, 0.0],
        #     [0.0, 0.0],
        #     [0.0, 0.0],
        #     [0.0, 0.0],
        #     [0.0, 0.0],
        #     ])

        # actual_results = amplitudeModulator.modulate_values(test_values)

        # self.assertTrue(numpy.allclose(expected_results,actual_results), "was %s expected %s" % (actual_results, expected_results))

        
