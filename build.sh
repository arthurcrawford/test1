#!/bin/bash

# Create a build directory
BUILD_DIR=build
mkdir -p "${BUILD_DIR}"

# Create component directory to stage raptly 
COMPONENT_DIR="${BUILD_DIR}"/raptly
mkdir -p "${COMPONENT_DIR}"

# Create assembly directories for packaging.
PACKAGE_DIR="${BUILD_DIR}"/package
PAYLOAD_DIR="${PACKAGE_DIR}"/payload
SCRIPT_DIR="${PACKAGE_DIR}"/scripts
mkdir -p "${PAYLOAD_DIR}"
mkdir -p "${SCRIPT_DIR}"

# Create Python virtualenv
PYTHON_VENV_NAME="${COMPONENT_DIR}"/python/venv
virtualenv --always-copy "${PYTHON_VENV_NAME}"

# Activate the virtualenv just created in the build dir
source "${PYTHON_VENV_NAME}"/bin/activate

# Upgrade pip inside the venv
pip install --upgrade pip

# Install python dependencies/requirements

# Copy our Python code to the virtual env's site-packages
# TODO - care maybe needed here - may not be python2.7. Can we find site-packages subdir first
MODULE_DIR="${PYTHON_VENV_NAME}"/lib/python2.7/site-packages/raptly/
mkdir -p "${MODULE_DIR}"
echo "Copying raptly code to ${MODULE_DIR}..."
cp src/main/python/raptly/*.py "${MODULE_DIR}"

cp src/assembly/postinstall "${SCRIPT_DIR}"

# Assemble the raptly python component payload
mkdir -p "${PAYLOAD_DIR}"/usr/local/opt/raptly/venv
cp -R "${COMPONENT_DIR}"/python/venv/* "${PAYLOAD_DIR}"/usr/local/opt/raptly/venv

# Copy wrapper script
mkdir -p "${PAYLOAD_DIR}"/usr/local/opt/raptly/bin
cp src/main/bin/raptly "${PAYLOAD_DIR}"/usr/local/opt/raptly/bin
