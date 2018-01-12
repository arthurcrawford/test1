# Docker base image for deb builds
FROM ubuntu:xenial
MAINTAINER Art
# Install typical pre-requisites for Debian package builds
RUN apt-get update && apt-get install -y \ 
    build-essential \
    autoconf \
    automake \
    autotools-dev \
    debhelper \
    dh-make \
    debmake \
    devscripts \
    fakeroot \
    file \
    git \
    gnupg \
    lintian \
    patch \
    patchutils \
    pbuilder \
    perl \
    python \
    quilt \
    curl \
    wget \
    tree \
    python-virtualenv \
    python-pip

COPY docker-entrypoint.sh /

ENTRYPOINT ["/docker-entrypoint.sh"]
