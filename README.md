Peachy Tool Chain
===============

NOTE: For usage instructions http://instructions.peachyprinter.com

NOTE To Developers: This version of the peachy printer code is depricated and a new code base has been created. As such pull requests outside of major bugs will not be considered.

This is the toolchain for producing prints with the Peachy Printer. It consists of 3 major tools:

* *calibrate* -- Interactive tool for drawing patterns and configuring tuning parameters to match the behaviour of your printer.
* *gcode_wav_converter* -- Converts gcode instructions into WAV and CUE files suitable for driving the Peachy Printer.
* *wav_player* -- Plays the WAV file while listening for drips to ensure that each layer is played at the right time.

Caveats
------------------------
* Major changes are to be expected to the structure and operation of all parts of this toolchain. Outside of bug fixes pull request are not recommended
* This code should not be used as an example for coding practices and standards.
* The next version of this software will be a complete rewrite.

Quick Start Guide
========================
This purpose of this guide should cover the basics of printing and will cover the following topics:

* Software installation
* Hardware setup
* Calibration
* Converting your model to gcode
* Converting your model to Peachy Printer format
* Printing you model


Future Development Plans (New Code Base)
========================

* Optional Blender Integration
* Print from Gcode directly
* Single file install no dependany install required
* Visually assited calibration
* Visually assisted printing
* Square pyrimid print area

Technical:

* Moving to a Onion Architecture 
** Seperate interface and api
* Moving to a fully TDD code base


Version History
------------------

2014-02-02 - Created this History
2014-03-27 - Depricated this code base