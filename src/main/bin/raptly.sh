#!/bin/bash
DEST_DIR=/usr/local/opt
VENV="${DEST_DIR}"/raptly/venv
source ${VENV}/bin/activate
SITE_PACKAGES="${VENV}"/lib/python2.7/site-packages
python ${SITE_PACKAGES}/raptly/raptly.py "$@"
