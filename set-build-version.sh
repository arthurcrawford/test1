#!/bin/bash
# Used by Makefile to substitute version number from Python _version.py into DEBIAN/control

# Extract the version from the Python version file
version=$(sed "s/[[:space:]]*__version__[[:space:]]*=[[:space:]]*\"\(.*\)\".*/\1/" raptly/_version.py)

# Substitute the version into the Debian control file
sed -i -e s/{__version__}/${version}/ build/raptly/DEBIAN/control