class CueFileWriter(object):
    FORMAT_VERSION = 1
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
        self.outfile.write('LOOPS_PER_LAYER %d\n' % loops_per_layer)
        self.outfile.write('LAYER_HEIGHT %f\n' % layer_height)
        self.outfile.write('BEGIN_CUES\n')

    def write_cue(self, frame):
        """Insert a cue marker for the given frame."""
        if not self._file_open:
            raise ValueError('File has already been closed.')
        self.outfile.write('%d\n' % frame)

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
    FORMAT_VERSION = 1
    def __init__(self, infile):
        """Provides read access to the data inside a CUE file."""
        self.infile = infile

        self.loops_per_layer = None
        self.layer_height = None
        self.cue_list_start_pos = None

        self._read_headers()

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
        parts = line.split(' ')
        if len(parts) != 2 or parts[0] != 'VERSION':
            raise ValueError('Syntax error: line 2 should contain "VERSION %d".')
        try:
            version = int(parts[1])
        except ValueError:
            raise ValueError('Syntax error: VERSION number should be an int, got %s' % parts[1])
        if version != self.FORMAT_VERSION:
            raise ValueError('Version mismatch: File is version %d, but this program requires version %d.' %
                             (version, self.FORMAT_VERSION))

        # Loops per layer
        line = self._read_nonblank_line()
        if not line:
            raise ValueError('Unexpected end of file looking for header "LOOPS_PER_LAYER".')
        parts = line.split(' ')
        if len(parts) != 2 or parts[0] != 'LOOPS_PER_LAYER':
            raise ValueError('Syntax error: line 3 should contain "LOOPS_PER_LAYER %d".')
        try:
            self.loops_per_layer = int(parts[1])
        except ValueError:
            raise ValueError('Syntax error: LOOPS_PER_LAYER number should be an int, got %s' % parts[1])

        # Layer height
        line = self._read_nonblank_line()
        if not line:
            raise ValueError('Unexpected end of file looking for header "LAYER_HEIGHT".')
        parts = line.split(' ')
        if len(parts) != 2 or parts[0] != 'LAYER_HEIGHT':
            raise ValueError('Syntax error: line 4 should contain "LAYER_HEIGHT %d".')
        try:
            self.layer_height = float(parts[1])
        except ValueError:
            raise ValueError('Syntax error: LAYER_HEIGHT number should be a float, got %s' % parts[1])

        # Cue list
        line = self._read_nonblank_line()
        if not line:
            raise ValueError('Unexpected end of file looking for header "BEGIN_CUES".')
        if line != 'BEGIN_CUES':
            raise ValueError('Syntax error: line 5 should contain "BEGIN_CUES".')
        self._cue_list_start_pos = self.infile.tell()

    def _read_nonblank_line(self):
        """Returns a non-empty line, or None if the end of the file is reached."""
        line = None
        while not line:
            line = self.infile.readline()
            if not line:
                return None
            line = line.strip().upper()
        return line

    def next(self):
        line = self._read_nonblank_line()
        if not line:
            raise ValueError('Unexpected end of file reading cue values.')
        if line == 'END_CUES':
            raise StopIteration()
        parts = line.split(' ')
        if not len(parts) == 1:
            raise ValueError('Syntax error: expected cue value or "END_CUES", got %s.' % line)
        try:
            frame = int(parts[0])
        except ValueError:
            raise ValueError('Syntax error: cue value should be an int, got %s' % parts[0])
        return frame

    def __iter__(self):
        return self
