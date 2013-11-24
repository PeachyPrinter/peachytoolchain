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
class PrinterParameters:
    """
    Parameters for your specific printer. Edit these as needed. Unless specified, distances are in
    millimeters.
    """
    WaveSamplingRate = 8000 # Value in samples per second (Hertz). The default should be more than enough.
    MaxFeedRate = 1200.0*60*10.0    # The maximum feed rate in millimeters per minute.
    ConstantFeedRate = False# If True, always use max feed rate instead of given rate
    XAxisChannel = 0        # These denote which channel of the WAV file is connected to which axis.
    YAxisChannel = 1        # Channel 0 is the left stereo audio channel, channel 1 is right.
    XAxisMinPos = 0.0     # Location in physical space (as defined in g-code) when the X-axis is set to
                            # the minimum possible audio output value.
    XAxisMaxPos = 25.4*10.0     # Location in physical space (as defined in g-code) when the X-axis is set to
                            # the maximum possible audio output value.
    YAxisMinPos = 0.0     # Location in physical space (as defined in g-code) when the Y-axis is set to
                            # the minimum possible audio output value.
    YAxisMaxPos = 25.4*10.0     # Location in physical space (as defined in g-code) when the Y-axis is set to
                            # the maximum possible audio output value.
    XDwellPos = 12.7*10.0      # Location in physical space where the X-axis will dwell between layers.
    YDwellPos = 12.7*10.0      # Location in physical space where the Y-axis will dwell between layers.
    XAxisMaxVel = 1200.0*60*10.0    # The maximum speed the laser can move along the X-axis in millimetres per minute.
    YAxisMaxVel = 1200.0*60*10.0    # The maximum speed the laser can move along the Y-axis in millimetres per minute.
    XAxisMaxAcc = 45000000.0*10.0*10.0    # The maximum acceleration of the X-axis in millimetres per second squared.
    YAxisMaxAcc = 45000000.0*10.0*10.0    # The maximum acceleration of the Y-axis in millimetres per second squared.
    TestTimeScale = 1.0     # Multiply all speeds by this amount. For testing only.

#### End of user-configurable parameters. Please do not modify anything below this line.

import math
import sys
import wave
from collections import deque
import cue_file
from audio.transform import AudioTransformer
from audio.tuning_parameter_file import TuningParameterFileHandler
from audio.util import convert_values_to_frames

MIN_STEP = 0.001*100.0 # Minimum possible step in millimetres. Used as a stopping condition.
DEBUG = False # Set to True for debugging messages
REPLAY_BUFFER_LEN = 93 # frames


class MachineState:
    """Represents the internal state of the machine, including position, velocity, and time."""
    x_pos = 0.0         # Current x and y position (in millimeters)
    y_pos = 0.0
    z_pos = 0.0         # z is special, since we have to wait for it, rather than control it
    x_vel = 0.0         # Current x and y velocity (in millimeters per second)
    y_vel = 0.0
    time = 0.0          # In seconds
    frame_num = 0       # Number of frames in the wav file. Tracked here because wave_write objects can't say.
    unit_scale = 1.0    # In units per millimetre. If set to inches, scale all movements by 25.4 mm/inch.
    extruder_pwm = 1.0  # The PWM fraction that the G-code was telling the printer to use. Since our printer
                        # can't adjust extrusion rate, we will have to scale the feed rate instead. 
    extruder_on = False # We need to rapid during a movement with extrusion off, since we can't turn off the laser.
    feed_rate = None    # The last requested feed rate in millimetres/minute. Saved in case a G-code doesn't specify it.
    replay_buffer = deque([], REPLAY_BUFFER_LEN)

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

    def __init__(self, printer_parameters):
        self.parameters = printer_parameters
        self.warned_once_codes = set()  # The set of codes that we have already warned the user are not supported.
        self.tuning_parameters = TuningParameterFileHandler.read_from_file('tuning.dat')
        self.transformer = AudioTransformer(self.tuning_parameters)

    def convertGcode(self, gcode_filename, wave_filename, cue_filename):
        wave_file = self.createWaveFile(wave_filename)
        cue_file = self.createCueFile(cue_filename)
        gcode_data = self.loadGcode(gcode_filename)
        state = MachineState()
        num_lines = len(gcode_data)
        lines_per_notify = int(num_lines / 100.0)
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
        wave_file.setframerate(self.parameters.WaveSamplingRate)
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
        except Exception as e:
            print("Exception while processing instruction '%s'" % gcode_instruction)
            raise
            
    def gCommandUseInches(self, params, state, wave_file, cue_file):
        state.unit_scale = 25.4     # millimetres per inch
        
    def gCommandUseMillimetres(self, params, state, wave_file, cue_file):
        state.unit_scale = 1.0      # millimetres is the base unit

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
                x_pos = float(param[1:]) * state.unit_scale
            elif param.startswith('Y'):
                y_pos = float(param[1:]) * state.unit_scale
            elif param.startswith('Z'):
                z_pos = float(param[1:]) * state.unit_scale
            elif param.startswith('F'):
                feed_rate = float(param[1:]) * state.unit_scale
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
            elif feed_rate > self.parameters.MaxFeedRate:
                print("WARNING: Requested feed rate %f mm/minute exceeds maximum machine feed rate %f mm/minute. "
                      "Clipping to maximum." % (feed_rate, self.parameters.MaxFeedRate))
            elif feed_rate / state.extruder_pwm > self.parameters.MaxFeedRate:
                print("WARNING: Effective feed rate %f mm/minute (based on requested feed rate %f mm/minute "
                      "and extruder PWM duty cycle %.1f%%) exceeds maximum machine feed rate %f mm/minute. "
                      "Clipping to maximum." % (feed_rate / state.extruder_pwm, feed_rate, state.extruder_pwm*100.0,
                          self.parameters.MaxFeedRate))
            state.feed_rate = feed_rate

        # 2. Determine what movement is being requested
        if z_pos is not None and z_pos != state.z_pos:
            # A new layer height has been requested. Move there first.
            self.moveToNewLayerHeight(z_pos, state, wave_file, cue_file)
        if x_pos is not None or y_pos is not None:
            # Lateral movement
            if x_pos > self.parameters.XAxisMaxPos:
                raise ValueError("Requested x position '%f' greater than machine maximum '%f'" % (x_pos, self.parameters.XAxisMaxPos)) 
            if x_pos < self.parameters.XAxisMinPos:
                raise ValueError("Requested x position '%f' less than machine minimum '%f'" % (x_pos, self.parameters.XAxisMinPos)) 
            if y_pos > self.parameters.YAxisMaxPos:
                raise ValueError("Requested y position '%f' greater than machine maximum '%f'" % (y_pos, self.parameters.YAxisMaxPos)) 
            if y_pos < self.parameters.YAxisMinPos:
                raise ValueError("Requested y position '%f' less than machine minimum '%f'" % (y_pos, self.parameters.YAxisMinPos)) 
            self.moveLateral(x_pos, y_pos, state, wave_file, rapid=False)
            
    def moveToNewLayerHeight(self, new_z_pos, state, wave_file, cue_file):
        if DEBUG:
            print('start new layer: time=%f, z_pos=%f' % (state.time, state.z_pos))
        if new_z_pos < state.z_pos:
            print("G-code requested us to move down Z axis, but we can't! Continuing at current height.")
            return
        dwell_time = 0.01 # seconds
        old_x_pos = state.x_pos
        old_y_pos = state.y_pos
        self.moveLateral(self.parameters.XDwellPos, self.parameters.YDwellPos, state, wave_file, rapid=True, record=False)
        dwell_mid_time = state.time + dwell_time/2.0
        dwell_end_time = state.time + dwell_time
        # Wait the first half of the time before inserting the cue
        while state.time < dwell_mid_time:
            self.addAudioFrame(self.parameters.XDwellPos, self.parameters.YDwellPos, 0.0, state, wave_file, record=False)
            step_time = (1.0/float(self.parameters.WaveSamplingRate))
            state.time += step_time
        state.z_pos = new_z_pos
        if DEBUG:
            print('insert layer break: time=%f, z_pos=%f' % (state.time, state.z_pos))
        cue_file.write_cue(state.frame_num)
        # Wait the second half of the time after inserting the cue
        while state.time < dwell_mid_time:
            self.addAudioFrame(self.parameters.XDwellPos, self.parameters.YDwellPos, 0.0, state, wave_file, record=False)
            step_time = (1.0/float(self.parameters.WaveSamplingRate))
            state.time += step_time
        # Move to the start of the replay buffer (f we have one yet)
        if state.replay_buffer:
            old_x_pos, old_y_pos, _ = state.replay_buffer.popleft()
        else:
            print('returning to last point: time=%f, x_pos=%f, y_pos=%f' % (state.time, old_x_pos, old_y_pos))
        self.moveLateral(old_x_pos, old_y_pos, state, wave_file, rapid=True, record=False)
        while True:
            try:
                x, y, z = state.replay_buffer.popleft()
            except IndexError:
                break
            self.addAudioFrame(x, y, z, state, wave_file, record=False)
            step_time = (1.0/float(self.parameters.WaveSamplingRate))
            state.time += step_time
        if DEBUG:
            print('end new layer: time=%f, z_pos=%f' % (state.time, state.z_pos))

    def moveLateral(self, x_pos, y_pos, state, wave_file, rapid=False, record=True):
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
        time_step = self.parameters.TestTimeScale / 60.0 / float(self.parameters.WaveSamplingRate)
        if DEBUG:
            print('delta_x=%f, delta_y=%f, distance=%f, cosine_x=%f, cosine_y=%f' % (
                (delta_x, delta_y, distance, cosine_x, cosine_y)))
        # 2. For each sample of the wave, calculate the position advanced to at the current feed rate
        while delta_x != 0.0 or delta_y != 0.0:
            if rapid:
                # Move as fast as possible while remaining coordinated
                # Determine max feed rate based on max axis velocities for this trajectory
                if cosine_y == 0.0:
                    max_feed = self.parameters.XAxisMaxVel
                elif cosine_x == 0.0:
                    max_feed = self.parameters.YAxisMaxVel
                else:
                    max_feed_from_x = self.parameters.XAxisMaxVel / abs(cosine_x)
                    max_feed_from_y = self.parameters.YAxisMaxVel / abs(cosine_y)
                    max_feed = min(max_feed_from_x, max_feed_from_y)
                feed_per_sample = max_feed*time_step
                max_step_x = feed_per_sample * abs(cosine_x)
                max_step_y = feed_per_sample * abs(cosine_y)
            else:
                # Use a constant speed with no acceleration and always move at requested feed rate
                assert state.extruder_pwm != 0.0, "If extruder_pwm=0, should rapid instead"
                feed_per_sample = (state.feed_rate/state.extruder_pwm)*time_step
                max_step_x = feed_per_sample * abs(cosine_x)
                max_step_y = feed_per_sample * abs(cosine_y)
            if abs(delta_x) > max_step_x:
                sample_delta_x = math.copysign(max_step_x, delta_x)
            else:
                sample_delta_x = delta_x
            if abs(delta_y) > max_step_y:
                sample_delta_y = math.copysign(max_step_y, delta_y)
            else:
                sample_delta_y = delta_y
            if DEBUG:
                print('sample_delta_x=%f, sample_delta_y=%f' % (sample_delta_x, sample_delta_y)) 
            state.x_pos += sample_delta_x
            state.y_pos += sample_delta_y
            state.time += time_step
            state.x_vel = sample_delta_x / time_step
            state.y_vel = sample_delta_y / time_step
            if DEBUG:
                print('time=%f, x_pos=%1.5f, y_pos=%1.5f, x_vel=%4.3f, y_vel=%4.3f' % (
                    state.time, state.x_pos, state.y_pos, state.x_vel, state.y_vel))
            self.addAudioFrame(state.x_pos, state.y_pos, state.z_pos, state, wave_file, record=record)
            delta_x -= sample_delta_x
            delta_y -= sample_delta_y
            if abs(delta_x) < MIN_STEP:
                delta_x = 0.0
            if abs(delta_y) < MIN_STEP:
                delta_y = 0.0
        # Always perform one sample while not moving so that velocity actually ends at zero.
        self.addAudioFrame(state.x_pos, state.y_pos, state.z_pos, state, wave_file)
        state.time += time_step
        state.x_vel = 0.0
        state.y_vel = 0.0
        if DEBUG:
            print('end move: time=%f, x_pos=%f, y_pos=%f' % (state.time, state.x_pos, state.y_pos))
            
    def addAudioFrame(self, x, y, z, state, wave_file, record=True):
        if record:
            state.replay_buffer.append((x, y, z))
        # Determine normalized space for points
        left = -1.0 + 2.0*(x-self.parameters.XAxisMinPos)/(self.parameters.XAxisMaxPos-self.parameters.XAxisMinPos)
        right = -1.0 + 2.0*(y-self.parameters.YAxisMinPos)/(self.parameters.YAxisMaxPos-self.parameters.YAxisMinPos)
        values = [(left, right)]
        # Transform according to tuning parameters
        values = self.transformer.transform_values(values)
        # Write to audio frames
        frames = convert_values_to_frames(values)
        wave_file.writeframesraw(frames)
        state.frame_num += 1

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


if len(sys.argv) != 4:
    print("Usage: %s <input.gcode> <output.wav> <output.cue>" % sys.argv[0])
    sys.exit(1)

parser = GcodeConverter(PrinterParameters())
print("Converting G-code file '%s' into wave file '%s' and cue file '%s'" % (sys.argv[1], sys.argv[2], sys.argv[3]))
parser.convertGcode(sys.argv[1], sys.argv[2], sys.argv[3])
