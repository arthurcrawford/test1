#!/bin/bash

BASE_DIR="${PWD}"
IDENTIFIER="com.a4pizza.raptly"
DEST_DIR=/usr/local/opt
COMPONENT="raptly"

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

# Create a component directory to stage code into
COMPONENT_DIR="${BUILD_DIR}/${COMPONENT}"
mkdir -p "${COMPONENT_DIR}"

# Create Python virtualenv and activate it
PYTHON_VENV_NAME="${COMPONENT_DIR}"/python/venv
virtualenv --always-copy "${PYTHON_VENV_NAME}"
source "${PYTHON_VENV_NAME}"/bin/activate

# Install python dependencies/requirements
pip install --upgrade pip

# Copy our Python code to the virtual env's site-packages
# Determine site packages dir for the virtualenv using distutils
SITE_PACKAGES=$(python -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")
MODULE_DIR="${SITE_PACKAGES}/${COMPONENT}/"
mkdir -p "${MODULE_DIR}"
cp src/main/python/${COMPONENT}/*.py "${MODULE_DIR}"

# Assemble the raptly python component payload; N.B. hidden files must be copied in this step!
mkdir -p "${PAYLOAD_DIR}${DEST_DIR}/${COMPONENT}"
cp -r "${COMPONENT_DIR}"/python/venv "${PAYLOAD_DIR}${DEST_DIR}/${COMPONENT}"/

# Fix the Python virtualenv path
sed -i.bak "s|$BUILD_DIR|$DEST_DIR|" "${PAYLOAD_DIR}${DEST_DIR}/${COMPONENT}"/venv/bin/activate
rm "${PAYLOAD_DIR}${DEST_DIR}/${COMPONENT}"/venv/bin/activate.bak

# Copy wrapper script
mkdir -p "${PAYLOAD_DIR}${DEST_DIR}/${COMPONENT}"/bin
cp src/main/bin/raptly "${PAYLOAD_DIR}${DEST_DIR}/${COMPONENT}"/bin

# Build OSX package
cp src/assembly/postinstall "${SCRIPT_DIR}"
pkgbuild \
 --root "${PAYLOAD_DIR}" \
 --scripts "${SCRIPT_DIR}" \
 --identifier "${IDENTIFIER}" \
 --version 1.0 "${BUILD_DIR}/${IDENTIFIER}".pkg
