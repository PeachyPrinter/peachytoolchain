echo "Strarting Calibration"
SET PATH=%PATH%;c:\Python27

REM Verifying Requirements

python --version
IF NOT ERRORLEVEL 0 (
    echo Python not found you may have to add it to your path
    set WILL_EXIT = 1
)

python -c 'import numpy'
IF NOT ERRORLEVEL 0 (
    echo numpy not installed
    set WILL_EXIT = 1
)

python -c 'import pyaudio'
IF NOT ERRORLEVEL 0 (
    echo pyaudio not installed
    set WILL_EXIT = 1
)

python -c 'import PySide'
IF NOT ERRORLEVEL 0 (
    echo PySide not installed
    set WILL_EXIT = 1
)

if WILL_EXIT == 1 (
    echo Requirement's not satisfied.
    echo Have your read INSTALL.md
    echo Exiting
    exit 1
)

echo "Requirments met"

pushd "%~dp0" 
python ..\src\calibrate-main.py
popd