"""gcode-wav file player
This program takes a wav file and its accompanying cue file (both converted to gcode from the gcode-to-wav converter)
and plays back each layer at the appropriate time. Between layers it holds the last position from the end of the
current layer. This relies on the gcode-to-wav converter leaving the laser at a safe spot at the layer break.

NOTE: This version uses a time per layer instead of counting drips.
"""
### Constants to edit while testing
INPUT_WAVE_RATE = 8000
DRIPS_PER_MILLIMETER = 170.0 # adjust this based on measurements of total drips and water level
MILLIMETER_PER_LAYER = 0.1 # Resolution as defined in slicer
MILLIMETER_PER_SUBLAYER = 0.01 # Resolution required to get proper adhesion -- this probably won't change

# Internal constants
DRIPS_PER_LAYER = DRIPS_PER_MILLIMETER*MILLIMETER_PER_LAYER
DRIPS_PER_SUBLAYER = DRIPS_PER_MILLIMETER*MILLIMETER_PER_SUBLAYER

import pyaudio
import math
import time
try:
    import queue
except:
    import Queue as queue
import sys
import wave

from cue_file import CueFileReader
from audio.drip_detector import DripDetector
from audio.util import STEREO_WAVE_STRUCT, MAX_S16

if not len(sys.argv) == 3:
    print("Usage: %s <wav_file> <cue_file>" % sys.argv[0])
    sys.exit(1)

wave_file = wave.open(sys.argv[1], 'rb')
if not wave_file.getnchannels() == 2:
    print("Error: wave file must be in stereo (2 channels)")
    sys.exit(1)
if not wave_file.getsampwidth() == 2:
    print("Error: wave file must be 16-bit")
    sys.exit(1)
wave_rate = wave_file.getframerate()

cue_file = CueFileReader(open(sys.argv[2], 'rt'))
# Make sure no advanced options are used yet, because we don't support them!
if cue_file.loops_per_layer != 1:
    print("Error: Current testing version doesn't support multiple loops per layer.")
    sys.exit(1)

pa = pyaudio.PyAudio()
outstream = pa.open(format=pa.get_format_from_width(2, unsigned=False),
                 channels=2,
                 rate=wave_rate,
                 output=True,
                 frames_per_buffer=int(wave_rate/8))
instream = pa.open(format=pa.get_format_from_width(2, unsigned=False),
                 channels=1,
                 rate=INPUT_WAVE_RATE,
                 input=True,
                 frames_per_buffer=int(INPUT_WAVE_RATE/8))
outstream.start_stream()
instream.start_stream()

#drip_file = wave.open('/home/james/peachy/experiments/drip_loop_fast.wav')

current_layer = 0
current_sublayer = 0
current_cue = 0
current_cue_file_pos = wave_file.tell() # Needed because the calculation for position is platform-dependent
current_frame_num = 0
next_cue = cue_file.next()
last_frame = STEREO_WAVE_STRUCT.pack(0, 0)
drip_detector = DripDetector(INPUT_WAVE_RATE)

print('Starting first layer')
try:
    while True:
        # Refill buffer as much as possible, stopping at cue point if present
        buffer_frames_available = outstream.get_write_available()
        if not buffer_frames_available:
            time.sleep(0.01)
            continue
        layer_frames_available = next_cue - current_frame_num
        num_layer_frames_to_write = min(layer_frames_available, buffer_frames_available)
        if num_layer_frames_to_write:
            frames = wave_file.readframes(num_layer_frames_to_write)
            last_frame = frames[-4:]
            outstream.write(frames)
            current_frame_num += num_layer_frames_to_write
            layer_frames_available -= num_layer_frames_to_write
            buffer_frames_available -= num_layer_frames_to_write
        # See if we need to fill the rest of the buffer with holding samples
        if buffer_frames_available and not layer_frames_available:
            hold_tuple = STEREO_WAVE_STRUCT.unpack(last_frame)
            hold_pos = (hold_tuple[0]/MAX_S16, hold_tuple[1]/MAX_S16)
            hold_frames = bytes(last_frame * buffer_frames_available)
            outstream.write(hold_frames)
        # Process audio input
        buffer_frames_available = instream.get_read_available()
        if buffer_frames_available:
            frames = instream.read(buffer_frames_available)
            ## Use fake data from a test input instead
            #frames = drip_file.readframes(buffer_frames_available)
            #frames_read = int(len(frames)/2)
            #if frames_read < buffer_frames_available:
            #    drip_file.rewind()
            #    frames += drip_file.readframes(buffer_frames_available-frames_read)
            drip_detector.add_frames(frames)
        # See if it's time to advance the layer
        layer_by_drips = int(math.floor(drip_detector.num_drips/DRIPS_PER_LAYER))
        if layer_by_drips > current_layer:
            # Always advance wave file to start of current layer to ensure we save start pos properly
            current_cue = next_cue
            if current_frame_num < current_cue:
                print('*** Ran out of time to finish the current sublayer before next layer!')
                wave_file.readframes(current_cue-current_frame_num)
            current_cue_file_pos = wave_file.tell()
            try:
                next_cue = cue_file.next()
            except StopIteration:
                break
            current_layer += 1
            print('Starting layer %d' % (current_layer+1))
        # See if it's time to advance the sublayer
        sublayer_by_drips = int(math.floor(drip_detector.num_drips/DRIPS_PER_SUBLAYER))
        if sublayer_by_drips > current_sublayer:
            if current_frame_num < next_cue:
                print('*** Ran out of time to finish the current sublayer before next sublayer!')
            # Rewind to start of current layer
            wave_file.setpos(current_cue_file_pos)
            current_frame_num = current_cue
            current_sublayer += 1
    print("Waiting for final layer to finish...")
finally:
    outstream.stop_stream()
    instream.stop_stream()
    outstream.close()
    instream.close()
    pa.terminate()