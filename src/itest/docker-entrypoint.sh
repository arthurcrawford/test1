#!/bin/bash
set -e

if [ "$1" = 'package' ]; then
    cd /root/src && make
elif [ "$1" = 'test' ]; then
    py.test
elif [ "$1" = 'serve' ]; then
    supervisord -c /etc/supervisor/supervisord.conf
else
    exec "$@"
fi
