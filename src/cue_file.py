import re

class CueFileWriter(object):
    FORMAT_VERSION = 2
    def __init__(self, outfile, loops_per_layer=1, layer_height=0.5):
        """Creates a CUE file writer.
        @params
            outfile -- file-like object -- Data will be written to this file.
            loops_per_layer -- int -- The number of times each layer should be played before moving to the next.
                This is recorded for the player's reference and is not otherwise used.
            layer_height -- float -- The layer height in millimeters.
                This is recorded for the player's reference and is not otherwise used.
        """
        self.outfile = outfile
        self._file_open = True
        self.outfile.write('CUE_FILE\n')
        self.outfile.write('VERSION %d\n' % self.FORMAT_VERSION)
        self.outfile.write('BEGIN_CUES\n')

    def write_cue(self, cue):
        """Insert a cue marker for the given frame."""
        if not self._file_open:
            raise ValueError('File has already been closed.')
        if cue.cue_type == CueTypes.PLAY:
            self.outfile.write('PLAY %d %d\n' % (cue.start_frame, cue.end_frame))
        elif cue.cue_type == CueTypes.LOOP_UNTIL_HEIGHT:
            self.outfile.write('LOOP %d %d UNTIL HEIGHT %f\n' % (cue.start_frame, cue.end_frame, cue.until_height))
        else:
            raise TypeError('Unrecognized cue type "%s"' % cue.cue_type)

    def close(self):
        if self._file_open:
            self.outfile.write('END_CUES\n')
            self.outfile.write('END\n')
            self._file_open = False

    def __del__(self):
        try:
            self.close()
        except:
            pass


class CueFileReader(object):
    FORMAT_VERSION = 2

    CUE_FILE_VERSION_RE = re.compile(r'''^VERSION (?P<version>[0-9.]+)$''')
    CUE_FILE_PLAY_CUE_RE = re.compile(r'''^PLAY (?P<start>[0-9]+) (?P<end>[0-9]+)$''', re.IGNORECASE)
    CUE_FILE_LOOP_UNTIL_HEIGHT_CUE_RE = re.compile(
        r'''^LOOP (?P<start>[0-9]+) (?P<end>[0-9]+) UNTIL HEIGHT (?P<height>[0-9.]+)$''', re.IGNORECASE)

    def __init__(self, infile):
        """Provides read access to the data inside a CUE file."""
        self.infile = infile

    def read_cues(self):
        """Returns a list of Cue objects correspending to the CUEs within the file"""
        self.infile.seek(0)
        self._read_headers()
        return [cue for cue in self._get_next_cue_generator]

    def _read_headers(self):
        # First line is CUE_FILE identifier
        line = self._read_nonblank_line()
        if not line:
            raise ValueError('Unexpected end of file looking for header "CUE_FILE".')
        if line != 'CUE_FILE':
            raise ValueError('This does not appear to be a CUE file. First line should say "CUE_FILE".')

        # Second line is VERSION number
        line = self._read_nonblank_line()
        if not line:
            raise ValueError('Unexpected end of file looking for header "VERSION".')
        match = CueFileReader.CUE_FILE_VERSION_RE.match(line)
        if not match:
            raise ValueError('Syntax error: expected "VERSION <version_number>", got "%s"' % (line,))
        version_str = match.group('version')
        try:
            version = int(version_str)
        except ValueError:
            raise ValueError('Syntax error: VERSION should have an integer version, got "%s"' % (version_str,))
        if version != self.FORMAT_VERSION:
            raise ValueError('Version mismatch: File is version %d, but this program requires version %d.' %
                             (version, self.FORMAT_VERSION))

        # Beginning of cue list
        line = self._read_nonblank_line()
        if not line:
            raise ValueError('Unexpected end of file looking for header "BEGIN_CUES".')
        if line != 'BEGIN_CUES':
            raise ValueError('Syntax error: expected "BEGIN_CUES", got "%s"', (line,))

    def _get_next_cue_generator(self):
        while True:
            line = self._read_nonblank_line()
            if not line:
                raise StopIteration()
            if line == 'END_CUES':
                raise StopIteration()
            match = CueFileReader.CUE_FILE_PLAY_CUE_RE.match(line)
            if match:
                yield self._parse_play_cue(match)
                continue
            match = CueFileReader.CUE_FILE_LOOP_UNTIL_HEIGHT_CUE_RE.match(line)
            if match:
                yield self._parse_loop_until_height_cue(match)
                continue
            raise ValueError('Syntax error: expected cue, got "%s"' % (line,))

    def _read_nonblank_line(self):
        """Returns a non-empty line, or None if the end of the file is reached."""
        line = None
        while not line:
            line = self.infile.readline()
            if not line:
                return None
            line = line.strip().upper()
        return line

    def _parse_play_cue(self, match):
        try:
            start_frame = int(match.group('start_frame'))
        except ValueError:
            raise ValueError('Syntax error: PLAY cue <start_frame> should be int; got "%s"' % (match.group('start_frame'),))
        try:
            end_frame = int(match.group('end_frame'))
        except ValueError:
            raise ValueError('Syntax error: PLAY cue <end_frame> should be int; got "%s"' % (match.group('end_frame'),))
        return PlayCue(start_frame, end_frame)

    def _parse_loop_until_height_cue(self, match):
        try:
            start_frame = int(match.group('start_frame'))
        except ValueError:
            raise ValueError('Syntax error: LOOP UNTIL HEIGHT cue <start_frame> should be int; got "%s"' % (match.group('start_frame'),))
        try:
            end_frame = int(match.group('end_frame'))
        except ValueError:
            raise ValueError('Syntax error: LOOP UNTIL HEIGHT cue <end_frame> should be int; got "%s"' % (match.group('end_frame'),))
        try:
            until_height = float(match.group('height'))
        except ValueError:
            raise ValueError('Syntax error: LOOP UNTIL HEIGHT cue <height> should be float; got "%s"' % (match.group('height'),))
        return LoopUntilHeightCue(start_frame, end_frame, until_height)


class CueTypes:
    PLAY = 'play'
    LOOP_UNTIL_HEIGHT = 'loop_until_height'

class Cue(object):
    cue_type = None
    start_frame = None
    end_frame = None

class PlayCue(Cue):
    cue_type = CueTypes.PLAY
    def __init__(self, start_frame, end_frame):
        self.start_frame = start_frame
        self.end_frame = end_frame

class LoopUntilHeightCue(Cue):
    cue_type = CueTypes.LOOP_UNTIL_HEIGHT
    def __init__(self, start_frame, end_frame, until_height):
        self.start_frame = start_frame
        self.end_frame = end_frame
        self.until_height = until_height
