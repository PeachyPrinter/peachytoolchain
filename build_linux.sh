#!/bin/bash

echo "------------------------------------"
echo "Cleaning workspace"
echo "------------------------------------"
rm -rf PeachyToolChain-*.tar
# TODO JT 2014-02-04 - Should clean the workspace

echo "------------------------------------"
echo "Extracting Git Revision Number"
echo "------------------------------------"

# TODO JT 2014-02-04 - Should extract the sematic file to  common place
SEMANTIC=0.0.1a

function trim() { echo $1; }

if [ -z $GIT_HOME ]; then
  if [ -f "/usr/local/bin/git" ]; then
    export GIT_HOME=/usr/local/bin/git
  elif [ -f "/usr/bin/git" ]; then
    export GIT_HOME=/usr/bin/git
  elif [ -f "/bin/git" ]; then
    export GIT_HOME=/bin/git
  else
    echo "Could not find git."
    exit 1
  fi
fi

export GIT_REV_COUNT_RAW=`$GIT_HOME log --pretty=oneline | wc -l`
export GIT_REV_COUNT=`trim $GIT_REV_COUNT_RAW`
export GIT_REV=`$GIT_HOME rev-parse HEAD`

VERSION=$SEMANTIC.$TAG$GIT_REV_COUNT
echo "Version: $VERSION"
echo "# THIS IS A GENERATED FILE " > version.properties
echo "version='$VERSION'" >> version.properties
echo "revision='$GIT_REV'" >> version.properties
echo "Git Revision Number is $GIT_REV_COUNT"
cp version.properties src/VERSION.py

echo "------------------------------------"
echo "Making files"
echo "------------------------------------"

make
if [ $? != 0 ]; then
    echo "FAILED BUILDING ABORTING"
    exit 55
fi

echo "------------------------------------"
echo "Running Tests"
echo "------------------------------------"

python test/tests.py
if [ $? != 0 ]; then
    echo "FAILED TESTS ABORTING"
    exit 55
fi


echo "------------------------------------"
echo "Create Peachy Tool Chain archive"
echo "------------------------------------"

tar cvf PeachyToolChain-$VERSION.tar README.md
tar rvf PeachyToolChain-$VERSION.tar licence.txt
tar rvf PeachyToolChain-$VERSION.tar src/
tar rvf PeachyToolChain-$VERSION.tar doc/
tar rvf PeachyToolChain-$VERSION.tar models/
tar rvf PeachyToolChain-$VERSION.tar audio_test_files/
tar rvf PeachyToolChain-$VERSION.tar bin/*.sh