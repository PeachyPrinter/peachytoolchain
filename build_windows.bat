echo "------------------------------------"
echo "Cleaning workspace"
echo "------------------------------------"

del PeachyToolChain-*.zip
REM TODO JT 2014-02-04 - Should clean the workspace

echo "------------------------------------"
echo "Extracting Git Revision Number"
echo "------------------------------------"

REM TODO JT 2014-02-04 - Should extract the sematic file to  common place
set SEMANTIC=0.0.1a

IF [NOT] DEFINED %GIT_HOME% (
  IF EXIST "/usr/local/bin/git" (
    set GIT_HOME=/usr/local/bin/git
  ) ELSE (
    echo "Could not find git."
    exit 1
  )
)

set GIT_REV_COUNT_RAW=`$GIT_HOME log --pretty=oneline | wc -l`
set GIT_REV_COUNT=`trim $GIT_REV_COUNT_RAW`
set GIT_REV=`$GIT_HOME rev-parse HEAD`

set VERSION=%SEMANTIC%.%TAG%%GIT_REV_COUNT%
echo "Version: $VERSION"
echo "# THIS IS A GENERATED FILE " > version.properties
echo "version='$VERSION'" >> version.properties
echo "revision='$GIT_REV'" >> version.properties
echo "Git Revision Number is %GIT_REV_COUNT%"
copy version.properties src/VERSION.py

echo "------------------------------------"
echo "Running Tests"
echo "------------------------------------"

python test/test.py

IF [NOT] ERRORLEVEL 0 (
    echo "FAILED TESTS ABORTING"
    exit 1
)


echo "------------------------------------"
echo "Making files"
echo "------------------------------------"

make

echo "------------------------------------"
echo "Create Peachy Tool Chain archive"
echo "------------------------------------"

REM tar cvf PeachyToolChain-$VERSION.tar README.md
REM tar rvf PeachyToolChain-$VERSION.tar licence.txt
REM tar rvf PeachyToolChain-$VERSION.tar src/
REM tar rvf PeachyToolChain-$VERSION.tar doc/
REM tar rvf PeachyToolChain-$VERSION.tar models/
REM tar rvf PeachyToolChain-$VERSION.tar audio_test_files/
REM tar rvf PeachyToolChain-$VERSION.tar bin/*.bat