Software Dependencies
=====================

In order to use the applications here, you will need Python as well as a few supporting libraries. Either Python 2 or 3 should work -- every effort has been made to support both simulatenously. The libraries used are:

* portaudio19
* PyAudio 0.27
* Qt 4.8.1 (other 4.x versions should work)
* PySide 1.1.0 (any version compatible with your Qt version should work)

The *calibrate* program will also need to have its UI files compiled using *pyside-uic*. There is a *Makefile* available in the *calibrate* directory to do this. Simply run:

    cd calibrate
    make


