#!/bin/bash

echo "Starting Calibration"
WORKING_DIRECTORY="${BASH_SOURCE%/*}"

# Verifying Requirements
python --version
if [ $? != 0 ]; then
    echo "Python not installed"
    WILL_EXIT=true
fi

python -c 'import numpy'
if [ $? != 0 ]; then
    echo "numpy not installed"
    WILL_EXIT=true
fi

python -c 'import pyaudio'
if [ $? != 0 ]; then
    echo "pyaudio not installed"
    WILL_EXIT=true
fi

python -c 'import PySide'
if [ $? != 0 ]; then
    echo "PySide not installed"
    WILL_EXIT=true
fi

if [ $WILL_EXIT ]; then
    echo "Requirement's not satisfied."
    echo "Have your read INSTALL.md"
    echo "Exiting"
    exit 1
fi

echo "Requirments met"
pushd $WORKING_DIRECTORY
python ../src/calibrate-main.py
popd
