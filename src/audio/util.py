import math
import struct
import numpy

STEREO_WAVE_STRUCT_FMT = '<hh'
STEREO_WAVE_STRUCT = struct.Struct(STEREO_WAVE_STRUCT_FMT)
MONO_WAVE_STRUCT_FMT = "h"
MONO_WAVE_STRUCT = struct.Struct(MONO_WAVE_STRUCT_FMT)
MAX_S16 = math.pow(2, 15)-1

def convert_values_to_frames(values):
    """Given a list of (left, right) audio values (normalized to [-1.0, 1.0]),
    return a string of bytes representing PCM frames for those values."""
    assert isinstance(values, numpy.ndarray) and values.shape[1] == 2
    values = numpy.rint(values*MAX_S16).astype(numpy.dtype('<i2'))
    return values.tostring()

def clip_values(values):
    assert isinstance(values, numpy.ndarray) and values.shape[1] == 2
    values = values.clip(-1.0, 1.0)
    return values