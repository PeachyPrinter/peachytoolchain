INSTALLATION 
==============

For the purpose of early access testing and development


Current Version
---------------
0.0.1.* alpha


Windows
---------------

* Install Python - choose the "Python 2.7.6 Windows Installer" link at http://python.org/download/
* Install PySide - download and install "PySide-1.2.1.win32-py2.7.exe" from  http://qt-project.org/wiki/PySide_Binaries_windows
* Install PyAudio - In the windows section select the option "PyAudio for Python 2.7" http://people.csail.mit.edu/hubert/pyaudio/#downloads
* Install numpy 2.8 - download and install http://www.numpy.org http://sourceforge.net/projects/numpy/files/NumPy/1.8.0/numpy-1.8.0-win32-superpack-python2.7.exe/download


Mac OSX
-------------------

Install xcode-select
Install Homebrew at the terminal
    
    ruby -e "$(curl -fsSL https://raw.github.com/Homebrew/homebrew/go/install)"

Install latest python

    brew install python

Install dependancies (Note this can take some time)
    
    brew install pyside
    brew install pyside-tools


Linux (debian)
---------------

Run the following from a terminal:
    
    sudo apt-get -y install python-numpy python-pyaudio python-PySide

Linux (RedHat)
---------------

Run the following from a terminal:
    
    sudo yum -y install python-numpy python-pyaudio python-PySide