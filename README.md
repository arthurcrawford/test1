# test1 ![build](https://travis-ci.org/arthurcrawford/test1.svg?branch=master)
Test1 repository for raptly tool

## Build
To build locally (Mac OSX or Debian/Linux)

    $ ./build.sh

To build a Debian archive in the support Docker container (Ubuntu:trusty).

    $ docker build -t raptly-support .
    
    $ BASEDIR=`pwd` && \
        docker run \
        -v ${BASEDIR}:/mnt/src \
        -v ${BASEDIR}/build:/mnt/build \
        -w /mnt/src \
        raptly-support build
  
## Test

To isolate yourself from other python environments on your system it's recommended to set up a virtualenv python environment first.  For example:

    $ virtualenv ~/venvs/test1
    $ source ~/venvs/test1/bin/activate

Then you may install pytest and execute the unit tests.

    $ pip install pytest
    $ PYTHONPATH=src/main/python pytest src/test/python

To run the integration tests (itests).

    $ ./itest.sh

## Install on Mac

with the GUI installer 

    $ open build/com.a4pizza.raptly.pkg
    
or a silent install, ignoring signing warnings
    
    $ sudo installer -allowUntrusted -verboseR -pkg build/com.a4pizza.raptly.pkg -target /

## Uninstall on Mac
    
    $ sudo rm -rf /usr/local/opt/raptly/
    $ sudo pkgutil --forget com.a4pizza.raptly
    
    
