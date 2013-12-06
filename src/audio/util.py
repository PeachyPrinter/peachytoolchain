import math
import struct

STEREO_WAVE_STRUCT_FMT = '<hh'
STEREO_WAVE_STRUCT = struct.Struct(STEREO_WAVE_STRUCT_FMT)
MONO_WAVE_STRUCT_FMT = "h"
MONO_WAVE_STRUCT = struct.Struct(MONO_WAVE_STRUCT_FMT)
MAX_S16 = math.pow(2, 15)-1

def convert_values_to_frames(values):
    """Given a list of (left, right) audio values (normalized to [-1.0, 1.0]),
    return a string of bytes representing PCM frames for those values."""
    array = bytearray()
    for left, right in values:
        try:
            array.extend(STEREO_WAVE_STRUCT.pack(int(left*MAX_S16), int(right*MAX_S16)))
        except struct.error:
            print('Failed to pack values (%f, %f)' % (left, right))
            raise
    return bytes(array)

def clip_values(values):
    new_values = []
    for (left, right) in values:
        left = min(1.0, max(-1.0, left))
        right = min(1.0, max(-1.0, right))
        new_values.append((left, right))
    return new_values