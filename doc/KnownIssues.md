Known Issues
============

There are a list of known issues that are being address:

* The combination of PyAudio and PySide/Qt results in random seg faults, even with no shared data. This can be easily reproduced using *calibrate* by removing the *time.sleep()* in the *AudioServer* loop. Changing the controls in the window will very often produce a segfault. Adding the sleep only makes this less likely, but it still occurs intermittently in practice.

* The *PrinterParameters* for the *gcode_to_wav_converter* are currently hard-coded internally. These will eventually be broken out into a separation configuration file.

* Picking values for the *PrinterParameters* is not obvious. There will eventually be a tool for coming up with these values experimentally.

* The tuning parameters provided by *calibrate* currently don't take the Z height into account. This will be added in the near future.

