# test1 ![build](https://travis-ci.org/arthurcrawford/test1.svg?branch=master)

Raptly is a release workflow tool and remote client for [aptly](https://www.aptly.info/), the Debian 
repository manager.

It is written in Python and is available for Mac (Homebrew) and Linux (Debian)

### Installation

#### Mac (Homebrew) 

Install: 

    $ brew tap a4pizza/oven
    $ brew install raptly

Upgrade:

    $ brew upgrade raptly

Uninstall:

    $ brew remove raptly

#### Linux (Debian)

    $ dpkg -i raptly_<version>_all.deb

### Configuration

Create a configuration file.

    $ cat ~/.raptly/config
    [default]
    url = "https://myrepo.example.com:9876/api"
    # Client cert authentication
    cert = "~/.raptly/client.crt"
    key = "~/.raptly/client.key"
    
    
    
    
    
    
    
    
    
    
    
    
    
    
## Development

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


    
#### The Mac component package (.pkg)

The build, when run on an OSX machine, will create a Mac (.pkg) file.  This can be useful in some 
circumstances if the Homebrew installation method is not possible. 

Install:

with the GUI installer 

    $ open build/com.a4pizza.raptly.pkg
    
or a silent install, ignoring signing warnings
    
    $ sudo installer -allowUntrusted -verboseR -pkg build/com.a4pizza.raptly.pkg -target /

Uninstall:
    
    $ sudo rm -rf /usr/local/opt/raptly/
    $ sudo pkgutil --forget com.a4pizza.raptly
    
    
    
    
    
    
    
