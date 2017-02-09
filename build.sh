#!/bin/bash

# Create a build directory
BUILD_DIR=build/raptly
mkdir -p "${BUILD_DIR}"

# Create assembly directory for packaging.
PACKAGE_DIR=build/package
PAYLOAD_DIR="${PACKAGE_DIR}/payload"
SCRIPT_DIR="${PACKAGE_DIR}/scripts"
mkdir -p "${PAYLOAD_DIR}"
mkdir -p "${SCRIPT_DIR}"

# Create Python virtualenv
PYTHON_VENV_NAME="${BUILD_DIR}/python/venv"
virtualenv --always-copy "${PYTHON_VENV_NAME}"

# Activate the virtualenv just created in the build dir
source "${PYTHON_VENV_NAME}/bin/activate"

# Upgrade pip inside the venv
pip install --upgrade pip

# Install python dependencies/requirements

# Copy our Python code to the virtual env's site-packages
# TODO - care maybe needed here - may not be python2.7. Can we find site-packages subdir first
MODULE_DIR="${PYTHON_VENV_NAME}/lib/python2.7/site-packages/raptly/"
mkdir -p "${MODULE_DIR}"
echo "Copying raptly code to ${MODULE_DIR}..."
cp src/main/python/raptly/*.py "${MODULE_DIR}"

cp src/assembly/postinstall "${SCRIPT_DIR}"
