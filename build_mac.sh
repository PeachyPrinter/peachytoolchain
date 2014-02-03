#!/bin/bash

echo "------------------------------------"
echo "Setting up Virtual Environment"
echo "------------------------------------"

cd src
virtualenv venv
source venv/bin/activate

# This should be in packaging
# pip install --upgrade PySide==1.2.1
pip install --upgrade mock==1.0.1
# pip install --upgrade pyaudio==0.2.7


cd ..

echo "------------------------------------------------"
echo "Running tests"
echo "------------------------------------------------"

cd test

python gcode_writer_test.py

if [ $? != 0 ]; then 
	echo "FAILURE OCCURED TESTING"
	exit 666
fi