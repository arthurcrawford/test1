# test1 ![build](https://travis-ci.org/arthurcrawford/test1.svg?branch=master)
Test1

## Build
To build locally

    ./build.sh

To build in the support Docker container (Ubuntu:trusty).

    BASEDIR=`pwd` && \
      docker run \
      -v ${BASEDIR}:/mnt/src \
      -v ${BASEDIR}/build:/mnt/build \
      -w /mnt/src \
      raptly build
  
## Test

To isolate yourself from other python environments on your system it's recommended to set up a virtualenv python environment first.  For example:

    virtualenv ~/venvs/test1
    source ~/venvs/test1/bin/activate

Then you may install pytest and execute the tests.

    pip install pytest
    PYTHONPATH=src/main/python pytest src/test/python

## Install on Mac

    open build/com.a4pizza.raptly.pkg

## Uninstall on Mac
    
    sudo rm -rf /usr/local/opt/raptly/
    sudo pkgutil --forget com.a4pizza.raptly
    
    