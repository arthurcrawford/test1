#!/bin/bash

BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
IDENTIFIER="com.a4pizza.raptly"
DEST_DIR=/usr/local/opt
COMPONENT="raptly"

BUILD_DIR="${BASE_DIR}"/build
PACKAGE_DIR="${BUILD_DIR}"/package
PAYLOAD_DIR="${PACKAGE_DIR}"/payload
SCRIPT_DIR="${PACKAGE_DIR}"/scripts
COMPONENT_DIR="${BUILD_DIR}/${COMPONENT}"
VENV_NAME=venv
VENV_DIR="${COMPONENT_DIR}"/"${VENV_NAME}"
ASSEMBLY_DIR="${PAYLOAD_DIR}${DEST_DIR}/${COMPONENT}"

# Create a clean build directory & subdirectories for assembly and packaging.
echo "Building in ${BUILD_DIR}..."
rm -rf "${BUILD_DIR}"
mkdir -p "${BUILD_DIR}"
mkdir -p "${PAYLOAD_DIR}"
mkdir -p "${SCRIPT_DIR}"
mkdir -p "${COMPONENT_DIR}"

# Create Python virtualenv, activate and install dependencies in it
virtualenv --always-copy --no-setuptools "${VENV_DIR}"
source "${VENV_DIR}"/bin/activate
python get-pip.py
pip install --upgrade pip
pip install -r requirements.txt

# Copy our Python code to the virtual env's site-packages
# Determine site packages directoryqq for the virtualenv using distutils
SITE_PACKAGES=$(python -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")
MODULE_DIR="${SITE_PACKAGES}/${COMPONENT}/"
mkdir -p "${MODULE_DIR}"
cp src/main/python/${COMPONENT}/*.py "${MODULE_DIR}"
VERSION=$(sed "s/[[:space:]]*__version__[[:space:]]*=[[:space:]]*\"\(.*\)\".*/\1/" "${MODULE_DIR}"/_version.py)
echo "Version: ${VERSION}"

# Assemble the raptly python component payload; N.B. hidden files must be copied in this step!
mkdir -p "${ASSEMBLY_DIR}"
cp -r "${VENV_DIR}" "${ASSEMBLY_DIR}"/
# Replace local path in venv activate with path of target location
sed -i.bak "s|$BUILD_DIR|$DEST_DIR|" "${ASSEMBLY_DIR}"/"${VENV_NAME}"/bin/activate
rm "${ASSEMBLY_DIR}"/"${VENV_NAME}"/bin/activate.bak

# Copy wrapper script
mkdir -p "${ASSEMBLY_DIR}"/bin
cp src/main/bin/raptly "${ASSEMBLY_DIR}"/bin

# Determine OS
case "$OSTYPE" in
  darwin*)  echo "Building OSX package" 
            # Build OSX package
            cp src/assembly/postinstall "${SCRIPT_DIR}"
            pkgbuild \
             --root "${PAYLOAD_DIR}" \
             --scripts "${SCRIPT_DIR}" \
             --identifier "${IDENTIFIER}" \
             --version 1.0 "${BUILD_DIR}/${IDENTIFIER}".pkg
            ;; 
  linux*)   echo "Building Debian package" 
            cp -R src/DEBIAN "${PAYLOAD_DIR}"
            cp src/assembly/postinstall "${PAYLOAD_DIR}"/DEBIAN/postinst
            # Substitute the version into the Debian control file
            sed -i -e s/{__version__}/${VERSION}/ "${PAYLOAD_DIR}"/DEBIAN/control
            # Build Debian package
            dpkg --build "${PAYLOAD_DIR}" "${BUILD_DIR}"
            ;;
  *)        echo "unknown: $OSTYPE" 
            echo "no packaging"
            ;;
esac

