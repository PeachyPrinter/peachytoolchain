@echo off

echo ------------------------------------
echo Cleaning workspace
echo ------------------------------------

del PeachyToolChain-*.zip
REM TODO JT 2014-02-04 - Should clean the workspace

echo ------------------------------------
echo Extracting Git Revision Number
echo ------------------------------------

REM TODO JT 2014-02-04 - Should extract the sematic file to  common place

set SEMANTIC=0.0.1a
IF NOT DEFINED GIT_HOME (
  git --version
  IF ERRORLEVEL 0 (
    set GIT_HOME=git
  ) ELSE (
    echo Could not find git.
    pause
    REM exit 1
  )
)

for /f "delims=" %%A in ('%GIT_HOME% rev-list HEAD --count') do set "GIT_REV_COUNT=%%A"
for /f "delims=" %%A in ('%GIT_HOME% rev-parse HEAD') do set "GIT_REV=%%A"

set VERSION=%SEMANTIC%.%GIT_REV_COUNT%
echo Version: %VERSION%
echo # THIS IS A GENERATED FILE  > version.properties
echo version='%VERSION%' >> version.properties
echo revision='%GIT_REV%' >> version.properties
echo Git Revision Number is %GIT_REV_COUNT%
copy version.properties src/VERSION.py


echo ------------------------------------
echo Making files
echo ------------------------------------

make
IF NOT ERRORLEVEL 0 (
    echo FAILED MAKE ABORTING
    exit 1
)

echo ------------------------------------
echo Running Tests
echo ------------------------------------

python test/tests.py
IF NOT ERRORLEVEL 0 (
    echo FAILED TESTS ABORTING
    exit 1
)

echo ------------------------------------
echo Create Peachy Tool Chain archive
echo ------------------------------------

7za a -tzip PeachyToolChain-%VERSION%.zip README.md
7za a -tzip PeachyToolChain-%VERSION%.zip licence.txt
7za a -tzip PeachyToolChain-%VERSION%.zip src/
7za a -tzip PeachyToolChain-%VERSION%.zip doc/
7za a -tzip PeachyToolChain-%VERSION%.zip models/
7za a -tzip PeachyToolChain-%VERSION%.zip audio_test_files/
7za a -tzip PeachyToolChain-%VERSION%.zip bin/*.bat