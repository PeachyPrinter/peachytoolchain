import numpy

class Plane2dTo3dAdapter(object):
    """
    Converts 2D (x,y) tuples into 3D (x,y,z) tuples using a constant Z value.
    """
    def __init__(self, generator, height):
        """
        generator -- Generator that returns 2D (x,y) point tuples
        height -- float -- The Z value to add to all 2D points to make 3D points
        """
        self.generator = generator
        self.height = height

    def nextN(self, n):
        points_2d = self.generator.nextN(n)
        z_array = numpy.ones((n, 1)) * self.height
        points_3d = numpy.column_stack((points_2d, z_array))
        return points_3d

