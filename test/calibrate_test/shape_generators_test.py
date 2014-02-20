import unittest
import sys
import os
import numpy
from testhelpers import TestHelpers

sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..', 'src', ))
from calibrate.shape_generators import NullGenerator
from calibrate.shape_generators import PathGenerator
from calibrate.shape_generators import ObjFileGenerator


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

class PathGeneratorTests(unittest.TestCase,TestHelpers):
    def setUp(self):
        self.sampling_rate = 2
        self.speed = 1.0
        self.size = 1.0
        self.center = (0,0)

    def test_should_draw_a_line(self):
        class HorizontalLineGenerator(PathGenerator):
            PATH = [(-1.0, 0.0), (1.0, 0.0)]

        expected = numpy.array([(0.0,0.0),(-0.5,0.0),(0.0,0.0),(0.5,0.0),(0.0,0.0),(-0.5,0.0)])
        generator = HorizontalLineGenerator(self.sampling_rate,self.speed,self.size,self.center)
        
        results = generator.nextN(6)

        self.assertNumpyArrayEquals(expected,results)

    def test_should_handle_case_when_path_on_vertex(self):
        class SquareLineGenerator(PathGenerator):
            PATH = [(0.0,0.0),(1.0,0.0),(1.0,1.0),(0.0,1.0)]

        expected = numpy.array([(0.0,0.0),(0.5,0.0),(0.5,0.5)])
        generator = SquareLineGenerator(self.sampling_rate,self.speed,self.size,self.center)
        
        results = generator.nextN(3)

        self.assertNumpyArrayEquals(expected,results)

    def test_should_handle_case_when_path_not_landing_on_vertex(self):
        class SquareLineGenerator(PathGenerator):
            PATH = [(0.0,0.0),(2.7,0.0),(2.7,2.7),(0.0,2.7)]

        expected = numpy.array( [(0.0,0.0),(0.45,0.0),(0.9,0.0),(1.35,0.0), (1.35,0.5)] )
        generator = SquareLineGenerator(self.sampling_rate,self.speed,self.size,self.center)
        
        results = generator.nextN(5)

        self.assertNumpyArrayEquals(expected,results)

    def test_should_go_as_far_as_possible_when_vertex_cannot_be_reached(self):
        class SquareLineGenerator(PathGenerator):
            PATH = [(0.0,0.0),(3.0,0.0),(3.0,3.0),(0.0,3.0)]

        expected = numpy.array( [(0.0,0.0),(0.5,0.0),(1.0,0.0)] )
        generator = SquareLineGenerator(self.sampling_rate,self.speed,self.size,self.center)
        
        results = generator.nextN(3)

        self.assertNumpyArrayEquals(expected,results)

    def test_should_go_as_far_as_possible_and_resume_when_vertex_cannot_be_reached(self):
        class SquareLineGenerator(PathGenerator):
            PATH = [(0.0,0.0),(3.0,0.0),(3.0,3.0),(0.0,3.0)]

        expected_1 = numpy.array( [(0.0,0.0),(0.5,0.0),(1.0,0.0)] )
        expected_2 = numpy.array( [(1.5,0.0),(1.5,0.5),(1.5,1.0)] )
        generator = SquareLineGenerator(self.sampling_rate,self.speed,self.size,self.center)
        
        results_1 = generator.nextN(3)
        self.assertNumpyArrayEquals(expected_1,results_1)

        results_2 = generator.nextN(3)
        self.assertNumpyArrayEquals(expected_2,results_2)

class ObjFileGeneratorTests(unittest.TestCase,TestHelpers):
    def setUp(self):
        self.sampling_rate = 2
        self.speed = 1.0
        self.size = 1.0
        self.center = (0,0)
        self.test_data_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..','test_data')

    def test_should_explode_if_no_file(self):
        fakefile = 'woot.obj'
        passed = False
        try:
            ObjFileGenerator(self.sampling_rate,self.speed,self.size,self.center,fakefile)
        except:
            passed = True
        self.assertTrue(passed)

    def test_should_explode_if_file_is_not_obj(self):
        file_path = os.path.join(self.test_data_folder,'notanobj.obj')
        passed = False
        try:
            ObjFileGenerator(self.sampling_rate,self.speed,self.size,self.center,file_path)
        except:
            passed = True
        self.assertTrue(passed)

    def test_should_load_points_for_simple_obj(self):
        file_path = os.path.join(self.test_data_folder,'simple.obj')
        generator = ObjFileGenerator(self.sampling_rate,self.speed,self.size,self.center,file_path)
        
        self.assertEquals(generator.PATH, [(-0.6,0.7),(0.4,0.7),(0.4,0.2),(-0.6,0.2)])
        
        expected = numpy.array( [(0.0,0.0),(-0.3,0.35),(0.2,0.35),(0.2,0.1),(-0.3,0.1),(-0.3,0.35)] )

        results = generator.nextN(6)
        self.assertNumpyArrayEquals(expected,results)



