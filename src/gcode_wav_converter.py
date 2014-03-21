#!/usr/bin/env python3
"""
Title: g-code to wav converter
Author: James Cooper <james@coopercs.ca>
Copyright: Rylan Grayston
License: GPLv2

This script converts g-code produced by Slic3r into a .wav file designed to drive the Peachy Printer.

To use this script, run it from the command line as follows:

    gcode_wav_converter.py tuning.dat input_file.gcode output_file.wav output_file.cue

This will load the gcode from input_file.gcode and create a an audio file output_file.wav and a cue file
output_file.cue. The audio will be such that the laser assembly of the Peachy Printer is moved appropriately
to draw the paths defined in the gcode. The cue file will be used by the player to determine the timing for each
chunk of audio to be played such that the build area Z changes appropriately.

In order for this script to produce audio appropriate for a printer, it must know several parameters of how audio
maps to movement of the laser for this specific printer. This is provided by the tuning.dat file, which can be created
using the laser calibration program.
"""
import math
import sys
import wave
import numpy

import cue_file as cue_file_mod
from audio.transform import PositionToAudioTransformer
from audio import modulation
from audio.tuning_parameter_file import TuningParameterFileHandler
from audio.util import convert_values_to_frames, clip_values
from util.gcode_layer_mixer import GCodeLayerMixer


WAVE_SAMPLING_RATE = 48000
DEBUG = False   # Set to True for debugging messages


class MachineState:
    """Represents the internal state of the machine, including position, velocity, and time."""
    x_pos = 0.0         # Current x and y position (in millimetres)
    y_pos = 0.0
    z_pos = 0.0         # z is special, since we have to wait for it, rather than control it
    time = 0.0          # In seconds
    feed_rate = None    # The last requested feed rate in millimetres/minute. Saved in case a G-code doesn't specify it.
    # The below are used to write the CUE file
    current_frame_num = 0   # Number of frames in the wav file. Tracked here because wave_write objects can't say.
    current_cue_start_frame_num = 0 # Frame number when the current cue started. Need to refer to it later when we know
                                    # where the end is.
    # The below are used to handle repeating a layer pattern for sublayering
    current_line_num = 0
    layer_start_x_pos = 0.0     # x and y position (in millimetres) at beginning of current layer
    layer_start_y_pos = 0.0
    layer_start_feed_rate = 0.0
    layer_start_line_num = 0 # Line number where current layer started
    drawing_sublayer = False    # True while we are looping to draw a sublayer


class GcodeConverter:
    KNOWN_GCODES = {
                    'G0': 'gCommandMove',
                    'G1': 'gCommandMove',
                    'G01': 'gCommandMove',
                    'G20': 'gCommandUseInches',
                    'G21': 'gCommandUseMillimetres',
                    'G28': 'gCommandMoveToOrigin',
                    'G90': 'gCommandUseAbsolutePositioning',
                   }

    def __init__(self, tuning_collection):
        self.tuning_collection = tuning_collection
        self.warned_once_codes = set()  # The set of codes that we have already warned the user are not supported.
        self.transformer = None
        self.modulator = None
        self.warnings = []

    def convertGcode(self, gcode_filename, wave_filename, cue_filename, flags = []):
        self.flags = flags
        self.transformer = self.createTransformer(self.tuning_collection)
        self.modulator = self.createModulator(self.tuning_collection)
        wave_file = self.createWaveFile(wave_filename)
        cue_file = self.createCueFile(cue_filename)
        gcode_data = self.loadGcode(gcode_filename)
        state = self.createInitialMachineState()
        num_lines = len(gcode_data)
        lines_per_notify = int(max(num_lines / 100.0, 1.0))
        while state.current_line_num < num_lines:
            line = gcode_data[state.current_line_num]
            if DEBUG:
                print('%07d: %s' % (state.current_line_num, line))
            if not state.drawing_sublayer and (state.current_line_num+1) % lines_per_notify == 0:
                print("Processing line %d of %d (%d%%)" % (
                    state.current_line_num+1, num_lines, int(math.ceil(100.0*(state.current_line_num+1)/num_lines))))
            if line:
                try:
                    self.processGcodeInstruction(line, wave_file, cue_file, state)
                except Exception:
                    print("Error processing line number %d" % state.current_line_num)
                    raise
            state.current_line_num += 1

    def createTransformer(self, tuning_collection):
        return PositionToAudioTransformer(tuning_collection)

    def createModulator(self, tuning_collection):
        return modulation.getModulator(tuning_collection.modulation, WAVE_SAMPLING_RATE)

    def createWaveFile(self, wave_filename):
        wave_file = wave.open(wave_filename, 'wb')
        wave_file.setnchannels(2)
        wave_file.setsampwidth(2)
        wave_file.setframerate(WAVE_SAMPLING_RATE)
        return wave_file

    def createCueFile(self, cue_filename):
        file = cue_file_mod.CueFileWriter(open(cue_filename, 'wt'))
        return file

    def loadGcode(self, gcode_filename):
        """Opens the given filename, reads the data in as ascii format, and strips all lines, returning
        a list of lines."""
        gcode_file = open(gcode_filename, 'rt')
        if 'm' in self.flags:
            return list(GCodeLayerMixer(gcode_file))
        else:
            gcode_data = [x.strip() for x in gcode_file.readlines()]
            return gcode_data

    def createInitialMachineState(self):
        return MachineState()

    def processGcodeInstruction(self, gcode_instruction, wave_file, cue_file, state):
        """Handles a single gcode_instruction, based on the current state, appending data to the
        wave_file as appropriate. The state will be updated to reflect the results after applying
        this instruction."""
        try:
            parts = gcode_instruction.split()
            command, params = parts[0], parts[1:]
            if command in self.KNOWN_GCODES:
                # Lookup the method for this command and perform it
                method = getattr(self, self.KNOWN_GCODES[command])
                method(params, state, wave_file, cue_file)
            elif command.startswith(';'):
                # Just a comment; skip it
                return
            elif command in self.warned_once_codes:
                # Already warned about this one
                return
            else:
                print("WARNING: Code %s is not currently supported and will be ignored." % command)
                self.warned_once_codes.add(command)
        except Exception:
            print("Exception while processing instruction '%s'" % gcode_instruction)
            raise

    def gCommandUseInches(self, params, state, wave_file, cue_file):
        raise ValueError('Command G20 (units in inches) is not supported. Please use millimetres.')

    def gCommandUseMillimetres(self, params, state, wave_file, cue_file):
        # This is the default; no processing necessary
        pass

    def to_mm_per_second(self, mm_per_minute):
        return mm_per_minute / 60.0

    def gCommandMove(self, params, state, wave_file, cue_file):
        # Moves from the current position to the position given in the params. This currently makes several
        # assumptions:
        # * Assumes that we are in absolute positioning mode (could be changed if necessary)
        
        # 1. Parse the params to determine what's being requested
        x_pos = None
        y_pos = None
        z_pos = None
        feed_rate = None
        extrude = False
        for param in params:
            if param.startswith('X'):
                x_pos = float(param[1:])
            elif param.startswith('Y'):
                y_pos = float(param[1:])
            elif param.startswith('Z'):
                z_pos = float(param[1:])
            elif param.startswith('F'):
                feed_rate = self.to_mm_per_second(float(param[1:]))
            elif param.startswith('E'):
                # The length of extrudate
                # HACK: We can't control amount of extrudate, but we use this to determine if extruding was
                # requested.
                extrude = True
            else:
                print("WARNING: Move command received unrecognized parameter '%s'; ignoring" % param)
        
        # Update feed rate if given
        if feed_rate is not None:
            # Check for validity of feed rate
            if feed_rate > self.tuning_collection.velocity_x_max:
                if not 'feed_rate_x' in self.warnings:
                    print("WARNING: Requested feed rate %f mm/second exceeds maximum machine X axis velocity of %f mm/second. "
                      "Clipping to maximum." % (feed_rate, self.tuning_collection.velocity_x_max))
                    self.warnings.append('feed_rate_x')
                feed_rate = self.tuning_collection.velocity_x_max
            if feed_rate > self.tuning_collection.velocity_y_max:
                if not 'feed_rate_y' in self.warnings:
                    print("WARNING: Requested feed rate %f mm/second exceeds maximum machine Y axis velocity of %f mm/second. "
                        "Clipping to maximum." % (feed_rate, self.tuning_collection.velocity_y_max))
                    self.warnings.append('feed_rate_y')
                feed_rate = self.tuning_collection.velocity_y_max
            state.feed_rate = feed_rate

        # 2. Determine what movement is being requested
        if x_pos is not None or y_pos is not None:
            # Lateral movement
            if x_pos > self.tuning_collection.build_x_max:
                raise ValueError("Requested x position '%f' greater than machine maximum '%f'" % (x_pos, self.tuning_collection.build_x_max))
            if x_pos < self.tuning_collection.build_x_min:
                raise ValueError("Requested x position '%f' less than machine minimum '%f'" % (x_pos, self.tuning_collection.build_x_min))
            if y_pos > self.tuning_collection.build_y_max:
                raise ValueError("Requested y position '%f' greater than machine maximum '%f'" % (y_pos, self.tuning_collection.build_y_max)) 
            if y_pos < self.tuning_collection.build_y_min:
                raise ValueError("Requested y position '%f' less than machine minimum '%f'" % (y_pos, self.tuning_collection.build_y_min))
            self.moveLateral(x_pos, y_pos, state, wave_file, extrude, rapid=False)
        if z_pos is not None and z_pos != state.z_pos:
            if x_pos is not None or y_pos is not None:
                if not 'lateralwarning' in self.warnings:
                    self.warnings.append('lateralwarning')
                    print('WARNING: Simultaneous lateral and vertical movements are not supported. Movements will be separated.')
            # A new layer height has been requested. Move there last so that new layer "starts" at end of this command.
            self.moveToNewLayerHeight(z_pos, state, wave_file, cue_file)

    def moveToNewLayerHeight(self, new_z_pos, state, wave_file, cue_file):
        if DEBUG:
            print('start new layer: time=%f, z_pos=%f' % (state.time, state.z_pos))
        if new_z_pos < state.z_pos:
            raise ValueError("G-code requested us to move down Z axis, but we can't!")
        # Algorithm:
        #   Move to dwell position
        #   Dwell for modulation period so we have something to loop over
        #   Move up one sublayer height
        #   If we need more sublayers:
        #       Loop back to the beginning of this layer (both position and gcode line)
        #   Else:
        #       Return to end of this layer and continue onward

        # Ensure every sublayer boundary is a multiple of the sublayer height, even if that means individual "layers"
        # don't necessarily line up with the exact Z height specified in gcode
        sublayer_height = self.tuning_collection.sublayer_height
        current_sublayer = int(round(state.z_pos/sublayer_height))
        end_sublayer = int(math.floor(new_z_pos/sublayer_height)) # Make sure we never pass requested height to avoid
                                                                  # false errors from next height request
        # Save state before move so we can restore afterwards
        layer_end_x_pos = state.x_pos
        layer_end_y_pos = state.y_pos

        # Move to dwell position
        self.moveLateral(self.tuning_collection.dwell_x, self.tuning_collection.dwell_y, state, wave_file, False, rapid=True)

        # Write the cue for the previous layer.
        cue_file.write_cue(cue_file_mod.PlayCue(state.current_cue_start_frame_num, state.current_frame_num))
        state.current_cue_start_frame_num = state.current_frame_num

        # Write one modulation period of dwell and add cue to loop until we reach the next sublayer
        num_samples = self.modulator.waveform_period
        samples = numpy.ones((num_samples, 3))
        samples *= numpy.array([state.x_pos, state.y_pos, state.z_pos])
        self.saveSamples(samples, state, wave_file, False)
        current_sublayer += 1
        state.z_pos = sublayer_height * current_sublayer
        cue_file.write_cue(cue_file_mod.LoopUntilHeightCue(
            state.current_cue_start_frame_num, state.current_frame_num, state.z_pos))
        state.current_cue_start_frame_num = state.current_frame_num

        if end_sublayer > current_sublayer:
            # Need to loop back to the start of this layer for another pass
            if DEBUG:
                print('Rewinding to beginning of layer to start next sublayer:\nz_pos=%f, current_sublayer=%d, end_sublayer=%d, layer_start_line_num=%d' % (
                    state.z_pos, current_sublayer, end_sublayer, state.layer_start_line_num
                ))
            state.drawing_sublayer = True
            self.moveLateral(state.layer_start_x_pos, state.layer_start_y_pos, state, wave_file, False, rapid=True)
            # Reset state to same as start of layer
            state.feed_rate = state.layer_start_feed_rate
            state.current_line_num = state.layer_start_line_num - 1  # This will be incremented before starting next instruction
        else:
            if DEBUG:
                print('''Reached requested height; continuing to next layer: z_pos=%f, current_sublayer=%d''' %(
                    state.z_pos, current_sublayer
                ))
            state.drawing_sublayer = False
            # Return to end of the current layer
            self.moveLateral(layer_end_x_pos, layer_end_y_pos, state, wave_file, False, rapid=True)
            # Save state at start of this layer
            state.layer_start_line_num = state.current_line_num + 1 # New layer starts after the vertical movement
            state.layer_start_x_pos = state.x_pos
            state.layer_start_y_pos = state.y_pos
            state.layer_start_feed_rate = state.feed_rate

    def moveLateral(self, x_pos, y_pos, state, wave_file, extrude, rapid=False):
        """Handles the actual controlled movement to an x,y position."""
        if DEBUG:
            print('start move: time=%f, start_x_pos=%f, start_y_pos=%f, end_x_pos=%f, end_y_pos=%f, extrude=%s, rapid=%s' % (
                state.time, state.x_pos, state.y_pos, x_pos, y_pos, extrude, rapid))
        delta_x = x_pos - state.x_pos
        delta_y = y_pos - state.y_pos
        distance = math.sqrt(math.pow(delta_x, 2.0) + math.pow(delta_y, 2.0))
        if distance <= 0.0:
            if DEBUG:
                print('No distance to move; returning')
            return
        cosine_x = delta_x / distance
        cosine_y = delta_y / distance
        if DEBUG:
            print('delta_x=%f, delta_y=%f, distance=%f, cosine_x=%f, cosine_y=%f' % (
                (delta_x, delta_y, distance, cosine_x, cosine_y)))
        if rapid:
            assert not extrude, "Extrude and rapid should be mutually exclusive!"
            # Move as fast as possible while remaining coordinated
            # Determine max feed rate based on max axis velocities for this trajectory
            if cosine_y == 0.0:
                max_feed = self.tuning_collection.velocity_x_max
            elif cosine_x == 0.0:
                max_feed = self.tuning_collection.velocity_y_max
            else:
                max_feed_from_x = self.tuning_collection.velocity_x_max / abs(cosine_x)
                max_feed_from_y = self.tuning_collection.velocity_y_max / abs(cosine_y)
                max_feed = min(max_feed_from_x, max_feed_from_y)
            feed_rate = max_feed
        else:
            # Use a constant speed with no acceleration and always move at requested feed rate
            feed_rate = state.feed_rate
        # To ensure exact distance is covered, create each sample by multiplying by the portion of the move made
        num_samples = int(math.ceil(distance * WAVE_SAMPLING_RATE / feed_rate))
        x_array = numpy.linspace(state.x_pos, state.x_pos+delta_x, num=num_samples)
        y_array = numpy.linspace(state.y_pos, state.y_pos+delta_y, num=num_samples)
        z_array = numpy.ones((num_samples,))*state.z_pos
        samples = numpy.column_stack((x_array, y_array, z_array))
        self.saveSamples(samples, state, wave_file, extrude)
        state.x_pos = state.x_pos+delta_x
        state.y_pos = state.y_pos+delta_y
        state.time += (len(samples) / WAVE_SAMPLING_RATE)

    def saveSamples(self, samples, state, wave_file, laser_enable):
        values = self.transformer.transform_points(samples)
        values = clip_values(values)
        # Only change laser enable if needed because it resets modulator
        if laser_enable != self.modulator.laser_enabled:
            self.modulator.laser_enabled = laser_enable
        values = self.modulator.modulate_values(values)
        frames = convert_values_to_frames(values)
        wave_file.writeframesraw(frames)
        if DEBUG:
            print('Wrote %d frames (%d - %d) with laser_enable=%s' % (len(samples), state.current_frame_num, len(samples)+state.current_frame_num, laser_enable))
        state.current_frame_num += len(samples)

    def gCommandUseAbsolutePositioning(self, params, state, wave_file, cue_file):
        # This is currently the only allowed value, so nothing needs to be done
        return
    
    def gCommandMoveToOrigin(self, params, state, wave_file, cue_file):
        # Move quickly to origin
        self.moveLateral(0.0, 0.0, state, wave_file, False, rapid=True)
        

def read_args():
    arg_list = []
    flags = []
    for arg in sys.argv[1:]:
        if arg.startswith('-'):
            flags.append(arg.split('-')[1])
        else:
            arg_list.append(arg)
    if len(arg_list) == 4:
        return { 'tuning' : arg_list[0], 'gcode': arg_list[1], 'wav': arg_list[2], 'cue': arg_list[3], 'flags' : flags}
    else:
        print("Usage: %s <tuning.dat> <input.gcode> <output.wav> <output.cue>" % sys.argv[0])
        print("Options:\n\t-m\tmix up gcode order")
        sys.exit(1)

args = read_args()

print args
print("Converting G-code file '%s' into wave file '%s' and cue file '%s', using tuning data file '%s'" % (args['gcode'], args['wav'], args['cue'], args['tuning']))

tuning_file_handler = TuningParameterFileHandler()
tuning_collection = tuning_file_handler.read_from_file(args['tuning'])
parser = GcodeConverter(tuning_collection)
parser.convertGcode(args['gcode'], args['wav'], args['cue'], args['flags'])
