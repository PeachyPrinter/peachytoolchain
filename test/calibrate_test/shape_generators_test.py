import unittest
import sys
import os
import numpy

sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..', 'src', ))
from calibrate.shape_generators import NullGenerator
from calibrate.shape_generators import PathGenerator


class NullGeneratorTests(unittest.TestCase):

    def test_NullGenerator_should_return_only_center_coordatates(self):
        sampling_rate = 44100
        speed = 100.0
        size = 10.0
        center = (0,0)
        generator = NullGenerator(sampling_rate,speed,size,center)

        self.assertTrue(numpy.array_equal(generator.nextN(1)[0], center))

        many_samples = generator.nextN(100)
        [ self.assertTrue(numpy.array_equal(sample, center)) for sample in many_samples ]


    def test_NullGenerator_should_handle_being_asked_for_no_samples(self):
        sampling_rate = 44100
        speed = 100.0
        size = 10.0
        center = (0,0)
        generator = NullGenerator(sampling_rate,speed,size,center)

        value = generator.nextN(0)

        self.assertEqual(len(value), 0)

