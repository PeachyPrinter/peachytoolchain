#!/usr/bin/env python3
"""
Title: g-code to wav converter
Author: James Cooper <james@coopercs.ca>
Copyright: Rylan Grayston
License: GPLv2

This script converts g-code produced by Skeinforge into a .wav file designed to drive Rylan's
stereolithographic 3D printer.

To use this script, run it from the command line as follows:

    gcode_wav_converter.py input_file.gcode output_file.wav

This will load the gcode from input_file.gcode and create a new file output_file.wav, overwriting any
existing output_file.

In order for the wav file to be useful to you, this script needs to know several parameters of your
particular printer. Please adjust these in the PrinterParameters class below.
"""
#### End of user-configurable parameters. Please do not modify anything below this line.

import math
import sys
import wave
import cue_file
import numpy
from audio.transform import PositionToAudioTransformer
from audio.tuning_parameter_file import TuningParameterFileHandler
from audio.util import convert_values_to_frames, clip_values

WAVE_SAMPLING_RATE = 44100
MIN_STEP = 0.001*100.0 # Minimum possible step in millimetres. Used as a stopping condition.
DEBUG = False # Set to True for debugging messages

class MachineState:
    """Represents the internal state of the machine, including position, velocity, and time."""
    x_pos = 0.0         # Current x and y position (in millimetres)
    y_pos = 0.0
    z_pos = 0.0         # z is special, since we have to wait for it, rather than control it
    time = 0.0          # In seconds
    frame_num = 0       # Number of frames in the wav file. Tracked here because wave_write objects can't say.
    extruder_pwm = 1.0  # The PWM fraction that the G-code was telling the printer to use. Since our printer
                        # can't adjust extrusion rate, we will have to scale the feed rate instead. 
    extruder_on = False # We need to rapid during a movement with extrusion off, since we can't turn off the laser.
    feed_rate = None    # The last requested feed rate in millimetres/minute. Saved in case a G-code doesn't specify it.

class GcodeConverter:
    KNOWN_GCODES = {
                    'G0': 'gCommandMove',
                    'G1': 'gCommandMove',
                    'G01': 'gCommandMove',
                    'G20': 'gCommandUseInches',
                    'G21': 'gCommandUseMillimetres',
                    'G28': 'gCommandMoveToOrigin',
                    'G90': 'gCommandUseAbsolutePositioning',
                    'M101': 'mCommandTurnExtruderOn',
                    'M103': 'mCommandTurnExtruderOff',
                    'M113': 'mCommandSetExtruderPWM',
                   }

    def __init__(self, tuning_collection):
        self.tuning_collection = tuning_collection
        self.warned_once_codes = set()  # The set of codes that we have already warned the user are not supported.
        self.transformer = PositionToAudioTransformer(self.tuning_collection)

    def convertGcode(self, gcode_filename, wave_filename, cue_filename):
        wave_file = self.createWaveFile(wave_filename)
        cue_file = self.createCueFile(cue_filename)
        gcode_data = self.loadGcode(gcode_filename)
        state = MachineState()
        num_lines = len(gcode_data)
        lines_per_notify = int(max(num_lines / 100.0, 1.0))
        for cur_line_num, line in enumerate(gcode_data):
            if DEBUG:
                print(line)
            if (cur_line_num+1) % lines_per_notify == 0:
                print("Processing line %d of %d (%d%%)" % (cur_line_num+1, num_lines, int(math.ceil(100.0*(cur_line_num+1)/num_lines))))
            if line:
                self.processGcodeInstruction(line, wave_file, cue_file, state)
        
    def createWaveFile(self, wave_filename):
        wave_file = wave.open(wave_filename, 'wb')
        wave_file.setnchannels(2)
        wave_file.setsampwidth(2)
        wave_file.setframerate(WAVE_SAMPLING_RATE)
        return wave_file

    def createCueFile(self, cue_filename):
        file = cue_file.CueFileWriter(open(cue_filename, 'wt'))
        return file

    def loadGcode(self, gcode_filename):
        """Opens the given filename, reads the data in as ascii format, and strips all lines, returning
        a list of lines."""
        gcode_file = open(gcode_filename, 'rt', encoding='ascii')
        gcode_data = [x.strip() for x in gcode_file.readlines()]
        return gcode_data
    
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

    def gCommandMove(self, params, state, wave_file, cue_file):
        # Moves from the current position to the position given in the params. This currently makes several
        # assumptions:
        # * Assumes that we are in absolute positioning mode (could be changed if necessary)
        
        # 1. Parse the params to determine what's being requested
        x_pos = None
        y_pos = None
        z_pos = None
        feed_rate = None
        for param in params:
            if param.startswith('X'):
                x_pos = float(param[1:])
            elif param.startswith('Y'):
                y_pos = float(param[1:])
            elif param.startswith('Z'):
                z_pos = float(param[1:])
            elif param.startswith('F'):
                feed_rate = float(param[1:]) / 60.0
            elif param.startswith('E'):
                # The length of extrudate -- ignore
                pass
            else:
                print("WARNING: Move command received unrecognized parameter '%s'; ignoring" % param)
        
        # Save specified feed rate or use the previous one if not specified
        if feed_rate is None:
            feed_rate = state.feed_rate
        else:
            # Check for validity of feed rate
            if state.extruder_pwm == 0.0:
                # Ignore feed rate, since we will rapid instead
                pass
            elif feed_rate > self.tuning_collection.velocity_x_max:
                print("WARNING: Requested feed rate %f mm/second exceeds maximum machine X axis velocity of %f mm/second. "
                      "Clipping to maximum." % (feed_rate, self.tuning_collection.velocity_x_max))
            elif feed_rate > self.tuning_collection.velocity_y_max:
                print("WARNING: Requested feed rate %f mm/second exceeds maximum machine Y axis velocity of %f mm/second. "
                      "Clipping to maximum." % (feed_rate, self.tuning_collection.velocity_y_max))
            elif feed_rate / state.extruder_pwm > self.tuning_collection.velocity_x_max:
                print("WARNING: Effective feed rate %f mm/second (based on requested feed rate %f mm/second "
                      "and extruder PWM duty cycle %.1f%%) exceeds maximum machine machine X axis velocity of %f mm/second. "
                      "Clipping to maximum." % (feed_rate / state.extruder_pwm, feed_rate, state.extruder_pwm*100.0,
                          self.tuning_collection.velocity_x_max))
            elif feed_rate / state.extruder_pwm > self.tuning_collection.velocity_y_max:
                print("WARNING: Effective feed rate %f mm/second (based on requested feed rate %f mm/second "
                      "and extruder PWM duty cycle %.1f%%) exceeds maximum machine machine Y axis velocity of %f mm/second. "
                      "Clipping to maximum." % (feed_rate / state.extruder_pwm, feed_rate, state.extruder_pwm*100.0,
                          self.tuning_collection.velocity_y_max))
            state.feed_rate = feed_rate

        # 2. Determine what movement is being requested
        if z_pos is not None and z_pos != state.z_pos:
            # A new layer height has been requested. Move there first.
            self.moveToNewLayerHeight(z_pos, state, wave_file, cue_file)
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
            self.moveLateral(x_pos, y_pos, state, wave_file, rapid=False)
            
    def moveToNewLayerHeight(self, new_z_pos, state, wave_file, cue_file):
        if DEBUG:
            print('start new layer: time=%f, z_pos=%f' % (state.time, state.z_pos))
        if new_z_pos < state.z_pos:
            print("G-code requested us to move down Z axis, but we can't! Continuing at current height.")
            return
        #:TODO: Laser off, move to dwell, wait one modulation cycle, return to position, laser on, and indicate loop frames
        state.z_pos = new_z_pos
        if DEBUG:
            print('insert layer break: time=%f, z_pos=%f' % (state.time, state.z_pos))
        cue_file.write_cue(state.frame_num)

    def moveLateral(self, x_pos, y_pos, state, wave_file, rapid=False):
        """Handles the actual controlled movement to an x,y position."""
        if DEBUG:
            print('start move: time=%f, start_x_pos=%f, start_y_pos=%f, end_x_pos=%f, end_y_pos=%f, rapid=%s' % (state.time, state.x_pos, state.y_pos, x_pos, y_pos, rapid))
        # Algorithm:
        # 1. Calculate distance and direction
        delta_x = x_pos - state.x_pos
        delta_y = y_pos - state.y_pos
        distance = math.sqrt(math.pow(delta_x, 2.0) + math.pow(delta_y, 2.0))
        if distance <= 0.0:
            print('No distance to move; returning')
            return
        cosine_x = delta_x / distance
        cosine_y = delta_y / distance
        if DEBUG:
            print('delta_x=%f, delta_y=%f, distance=%f, cosine_x=%f, cosine_y=%f' % (
                (delta_x, delta_y, distance, cosine_x, cosine_y)))
        if rapid:
            #:TODO: Disable laser during rapid
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
            assert state.extruder_pwm != 0.0, "If extruder_pwm=0, should rapid instead"
            feed_rate = state.feed_rate / state.extruder_pwm
        # To ensure exact distance is covered, create each sample by multiplying by the portion of the move made
        num_samples = int(math.ceil(distance * WAVE_SAMPLING_RATE / feed_rate))
        x_array = numpy.linspace(state.x_pos, state.x_pos+delta_x, num=num_samples)
        y_array = numpy.linspace(state.y_pos, state.y_pos+delta_y, num=num_samples)
        z_array = numpy.ones((num_samples,))*state.z_pos
        samples = numpy.column_stack((x_array, y_array, z_array))
        self.saveSamples(samples, state, wave_file)
        state.x_pos = state.x_pos+delta_x
        state.y_pos = state.y_pos+delta_y
        state.time += (len(samples) / WAVE_SAMPLING_RATE)

    def saveSamples(self, samples, state, wave_file):
        values = self.transformer.transform_points(samples)
        values = clip_values(values)
        frames = convert_values_to_frames(values)
        wave_file.writeframesraw(frames)
        state.frame_num += len(samples)

    def mCommandSetExtruderPWM(self, params, state, wave_file, cue_file):
        pwm_rate = None
        for param in params:
            if param.startswith('S'):
                try:
                    rate = float(param[1:])
                except ValueError:
                    raise ValueError("Command received malformed parameter '%s'; expected a float" % param)
                pwm_rate = rate
            else:
                print("WARNING: SetExtruderPWM received unrecognized parameter '%s'" % param)
        if pwm_rate is not None:
            state.extruder_pwm = pwm_rate
    
    def gCommandUseAbsolutePositioning(self, params, state, wave_file, cue_file):
        # This is currently the only allowed value, so nothing needs to be done
        return
    
    def gCommandMoveToOrigin(self, params, state, wave_file, cue_file):
        # Move quickly to origin
        self.moveLateral(0.0, 0.0, state, wave_file, rapid=True)
        
    def mCommandTurnExtruderOn(self, params, state, wave_file, cue_file):
        state.extruder_on = True
    
    def mCommandTurnExtruderOff(self, params, state, wave_file, cue_file):
        state.extruder_on = False


if len(sys.argv) != 5:
    print("Usage: %s <tuning.dat> <input.gcode> <output.wav> <output.cue>" % sys.argv[0])
    sys.exit(1)

print("Converting G-code file '%s' into wave file '%s' and cue file '%s', using tuning data file '%s'" % (sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[1]))

tuning_file_handler = TuningParameterFileHandler()
tuning_collection = tuning_file_handler.read_from_file(sys.argv[1])
parser = GcodeConverter(tuning_collection)
parser.convertGcode(sys.argv[2], sys.argv[3], sys.argv[4])
