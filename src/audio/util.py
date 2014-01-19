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
    array = bytearray(STEREO_WAVE_STRUCT.size * len(values))
    [STEREO_WAVE_STRUCT.pack_into(array, i*STEREO_WAVE_STRUCT.size, int(MAX_S16*values[i][0]), int(MAX_S16*values[i][1]))
     for i in range(len(values))]
    return bytes(array)

def clip_values(values):
    new_values = [(
                      min(1.0, max(-1.0, values[i][0])),
                      min(1.0, max(-1.0, values[i][1]))
                  ) for i in range(len(values))]
    return new_values