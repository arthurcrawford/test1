#!/bin/bash

BASE_DIR="${PWD}"

# Create a clean build directory
BUILD_DIR="${BASE_DIR}"/build
rm -rf "${BUILD_DIR}"
mkdir -p "${BUILD_DIR}"
echo "Building in ${BUILD_DIR}..."

# Create subdirectories for assembly and packaging.
PACKAGE_DIR="${BUILD_DIR}"/package
PAYLOAD_DIR="${PACKAGE_DIR}"/payload
SCRIPT_DIR="${PACKAGE_DIR}"/scripts
mkdir -p "${PAYLOAD_DIR}"
mkdir -p "${SCRIPT_DIR}"

# Create a component directory to stage raptly code into
COMPONENT_DIR="${BUILD_DIR}"/raptly
mkdir -p "${COMPONENT_DIR}"

# Create Python virtualenv and activate it
PYTHON_VENV_NAME="${COMPONENT_DIR}"/python/venv
virtualenv --always-copy "${PYTHON_VENV_NAME}"
source "${PYTHON_VENV_NAME}"/bin/activate

# Install python dependencies/requirements
pip install --upgrade pip

# Copy our Python code to the virtual env's site-packages
# TODO - care maybe needed here - may not be python2.7. Can we find site-packages subdir first
MODULE_DIR="${PYTHON_VENV_NAME}"/lib/python2.7/site-packages/raptly/
mkdir -p "${MODULE_DIR}"
cp src/main/python/raptly/*.py "${MODULE_DIR}"

# Assemble the raptly python component payload; N.B. hidden files must be copied in this step!
mkdir -p "${PAYLOAD_DIR}"/usr/local/opt/raptly
cp -r "${COMPONENT_DIR}"/python/venv "${PAYLOAD_DIR}"/usr/local/opt/raptly/

# Fix the Python virtualenv path
sed -i.bak "s|$BUILD_DIR|/usr/local/opt|" "${PAYLOAD_DIR}"/usr/local/opt/raptly/venv/bin/activate

# Copy wrapper script
mkdir -p "${PAYLOAD_DIR}"/usr/local/opt/raptly/bin
cp src/main/bin/raptly "${PAYLOAD_DIR}"/usr/local/opt/raptly/bin

# Build OSX package
cp src/assembly/postinstall "${SCRIPT_DIR}"
pkgbuild \
 --root "${PAYLOAD_DIR}" \
 --scripts "${SCRIPT_DIR}" \
 --identifier com.a4pizza.raptly \
 --version 1.0 "${BUILD_DIR}"/raptly.pkg
