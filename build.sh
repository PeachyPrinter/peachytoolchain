#!/bin/bash

echo "------------------------------------------------"
echo "Running tests"
echo "------------------------------------------------"

cd test

python gcode_writer_test.py

if [ $? != 0 ]; then 
	echo "FAILURE OCCURED TESTING"
	exit 666
fi