peachytoolchain
===============

This is the toolchain for producing prints with the Peachy Printer. It consists of 3 major tools:

* *calibrate* -- Interactive tool for drawing patterns and configuring tuning parameters to match the behaviour of your printer.
* *gcode_wav_converter* -- Converts gcode instructions into WAV and CUE files suitable for driving the Peachy Printer.
* *wav_player* -- Plays the WAV file while listening for drips to ensure that each layer is played at the right time.

This code is still in an alpha state. Major changes are to be expected to the structure and operation of all parts of this toolchain.

