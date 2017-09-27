# Docker base image for deb builds
FROM ubuntu:trusty
MAINTAINER Art

RUN echo "deb http://repo.aptly.info/ squeeze main" >> /etc/apt/sources.list.d/aptly.list
COPY aptly_pubkey.txt /
RUN apt-key add aptly_pubkey.txt && \
      DEBIAN_FRONTEND=noninteractive apt-get update && apt-get install -y --no-install-recommends \
      apt-utils \
      aptly \
      bzip2 \
      nginx \
      supervisor \
      vim \
      xz-utils \
   && rm -rf /var/lib/apt/lists/*

VOLUME ["/root/src"]
ENV PYTHONPATH="/root/src"

COPY program_aptly_api.conf /etc/supervisor/conf.d
COPY docker-entrypoint.sh /
COPY supervisord.conf /etc/supervisor
COPY gpg_private.asc /
COPY gpg_public.asc /
RUN /usr/bin/gpg --import gpg_private.asc

COPY docker-entrypoint.sh /

ENTRYPOINT ["/docker-entrypoint.sh"]
