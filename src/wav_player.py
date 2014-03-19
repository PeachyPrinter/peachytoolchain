#!/usr/bin/env python3
"""
Title: wav player
Author: James Cooper <james@coopercs.ca>
Copyright: Rylan Grayston
License: GPLv2

This program takes a wav file and its accompanying cue file (both converted from gcode with the gcode-to-wav converter)
and plays back each layer.
"""

## Parameters for debugging
USE_VIRTUAL_DRIP = False    # If True, mic input will be ignored and a constant drip rate will be assumed.
VIRTUAL_DRIP_RATE = 1.0     # drips per second
DEBUG = False               # If True, additional debugging information will be printed
TRACE = False               # If True, all cue and frame count information will be printed (VERY NOISY)
DEBUG_STREAM = False        # If True, will save all wave output to a file for review

# Internal constants
INPUT_WAVE_RATE = 48000

import pyaudio
import time
try:
    import queue
except:
    import Queue as queue
import sys
import wave

import cue_file as cue_file_mod
from audio.drip_detector import DripDetector, VirtualDripDetector
from audio.tuning_parameter_file import TuningParameterFileHandler
from util.logging import Logging

drip_governor = None

if TRACE:
    log_level = 'TRACE'
else:
    log_level = 'INFO'

log = Logging(level=log_level)

# Parse command line arguments
if len(sys.argv) == 4:
    tuning_filename, wave_file_name, cue_file_name = sys.argv[1:]
elif len(sys.argv) == 5:
    from util.drip_governor import DripGovernor
    tuning_filename, wave_file_name, cue_file_name, port = sys.argv[1:]
    drip_governor = DripGovernor(port)
    print('importing drip gov')
else:
    print("Usage: %s <tuning.dat> <output.wav> <output.cue>" % sys.argv[0])
    sys.exit(1)

# Loading tuning parameters
tuning_collection = TuningParameterFileHandler.read_from_file(tuning_filename)

# Open the wave file
wave_file = wave.open(wave_file_name, 'rb')
if not wave_file.getnchannels() == 2:
    log.error("Error: wave file must be in stereo (2 channels)")
    sys.exit(1)
if not wave_file.getsampwidth() == 2:
    log.error("Error: wave file must be 16-bit")
    sys.exit(1)
wave_rate = wave_file.getframerate()

# Read the cues from the cue file
cue_file = cue_file_mod.CueFileReader(open(cue_file_name, 'rt'))
cues = cue_file.read_cues()
del cue_file

# Setup the audio interface
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

# wave_file uses platform-dependent positions, so we can't seek directly to a position unless we first visit it
# and save our current position
frame_position_cache = {} # frame_num : wave.tell() platform-dependent position value

if USE_VIRTUAL_DRIP:
    drip_detector = VirtualDripDetector(INPUT_WAVE_RATE, VIRTUAL_DRIP_RATE)
else:
    drip_detector = DripDetector(INPUT_WAVE_RATE, debug=DEBUG)

# Initialize cue/frame state
current_cue_index = 0
current_cue = cues[current_cue_index]
current_frame_num = 0
frame_position_cache[current_frame_num] = wave_file.tell()

if DEBUG_STREAM:
    debug_outfile = wave.open('./debug.wav', 'wb')
    debug_outfile.setnchannels(2)
    debug_outfile.setframerate(wave_rate)
    debug_outfile.setsampwidth(2)

## Main loop for recording/playback
log.info('Playing %d cues...' % len(cues))
try:
    while True:
        # Process audio input
        buffer_frames_available = instream.get_read_available()
        if buffer_frames_available:
            frames = instream.read(buffer_frames_available)
            drip_detector.add_frames(frames)
        # Determine output
        buffer_frames_available = outstream.get_write_available()
        if not buffer_frames_available:
            # If no room in buffer, check again later
            time.sleep(0.01)
            continue
        # Fill the buffer, using multiple cues if necessary
        while buffer_frames_available:
            # Use as many frames as possible from the current cue, up to the amount of room left
            cue_frames_available = current_cue.end_frame - current_frame_num
            num_frames_to_play = min(buffer_frames_available, cue_frames_available)
            if TRACE:
                print('cue_frames_available=%d, buffer_frames_available=%d, num_frames_to_play=%d' % (
                    cue_frames_available, buffer_frames_available, num_frames_to_play
                ))
            if num_frames_to_play:
                frames = wave_file.readframes(num_frames_to_play)
                current_frame_num += num_frames_to_play
                if TRACE:
                    print('read %d frames (%d bytes); current_frame_num=%d' % (
                        num_frames_to_play, len(frames), current_frame_num
                    ))
                outstream.write(frames)
                if DEBUG_STREAM:
                    debug_outfile.writeframes(frames)
            buffer_frames_available -=  num_frames_to_play
            # If we exhausted this cue, determine which one to use next
            if current_frame_num == current_cue.end_frame:
                if TRACE:
                    print('reached end of current cue')
                # If we're in a LOOP_UNTIL_HEIGHT cue, see if we should loop or continue onward
                current_height = float(drip_detector.num_drips) / tuning_collection.drips_per_height
                if (current_cue.cue_type == cue_file_mod.CueTypes.LOOP_UNTIL_HEIGHT
                        and current_height < current_cue.until_height):
                    if TRACE:
                        print('relooping current cue back to frame %d' % (current_cue.start_frame,))
                    # Loop back to the start of this cue
                    current_frame_num = current_cue.start_frame
                    wave_pos = frame_position_cache[current_frame_num]
                    wave_file.setpos(wave_pos)
                    log.info("Waiting for drips")
                    if drip_governor:
                        drip_governor.start_dripping()
                else:
                    if (current_cue.cue_type == cue_file_mod.CueTypes.LOOP_UNTIL_HEIGHT and current_height > current_cue.until_height):
                        # log.warning("Dripping Too Fast Current: %s Cue: %s ahead by:  %.2f" % (current_height, current_cue.until_height, (current_height - current_cue.until_height)))
                        ahead_by_mm = current_height - current_cue.until_height
                        ahead_by_drips = int(ahead_by_mm * tuning_collection.drips_per_height)
                        log.warning('Too fast: '+'-' * ahead_by_drips + "> %d drips ahead" % ahead_by_drips)
                        if drip_governor:
                            if ahead_by_drips > 10:
                                drip_governor.stop_dripping()
                                print('------Stop Dripping!-----')
                            elif ahead_by_drips < 5:
                                drip_governor.start_dripping()
                                print('+++++Start Dripping!+++++')
                    # Advance to next cue
                    current_cue_index += 1
                    if current_cue_index >= len(cues):
                        # We've reached the end and can now exit
                        raise StopIteration('Reached end of cue list')
                    current_cue = cues[current_cue_index]
                    log.info('Playing cue %d of %d (%2.1f%%)' % (
                        current_cue_index+1, len(cues), 100.0*float(current_cue_index+1)/float(len(cues))
                    ))
                    if DEBUG:
                        print('Height = %0.3f' % current_height)
                    # How do we get to the new cue position?
                    new_frame_num = current_cue.start_frame
                    if new_frame_num in frame_position_cache:
                        # Use cached position
                        wave_pos = frame_position_cache[new_frame_num]
                        if TRACE:
                            print('New position in cache; frame_num=%d, wave_pos=%d' % (new_frame_num, wave_pos))
                        wave_file.setpos(wave_pos)
                    elif new_frame_num >= current_frame_num:
                        # Advance by reading and discarding frames
                        num_frames_to_discard = new_frame_num - current_frame_num
                        if TRACE:
                            print('Need to fast-forward to find new position: num_frames_to_discard=%d (%d-%d)' % (
                                num_frames_to_discard, new_frame_num, current_frame_num
                            ))
                        if num_frames_to_discard:
                            wave_file.readframes(num_frames_to_discard)
                    else:
                        if DEBUG:
                            print('WARNING: Was forced to rewind to seek to frame_num=%d' % new_frame_num)
                        wave_file.rewind()
                        wave_file.readframes(new_frame_num)
                    current_frame_num = new_frame_num
                    # Save the new start position to the cache (since we're likely to loop back to it)
                    frame_position_cache[current_frame_num] = wave_file.tell()
                # NOTE: Don't read and play frames yet; will be handled when loop continues
except StopIteration:
    log.info('Finished playing final cue; waiting for playback to complete.')
finally:
    # Stop audio interface
    outstream.stop_stream()
    instream.stop_stream()
    outstream.close()
    instream.close()
    pa.terminate()
    if drip_governor:
        drip_governor.stop_dripping()
        print('------Stop Dripping!-----')
        drip_governor.close()
    if DEBUG_STREAM:
        debug_outfile.close()
