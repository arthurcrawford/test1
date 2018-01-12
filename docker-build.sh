#!/bin/bash

docker build -t raptly-support .

BASEDIR=`pwd` && \
  docker run \
  -v ${BASEDIR}:/mnt/src \
  -v ${BASEDIR}/build:/mnt/build \
  -w /mnt/src \
  raptly-support build
