#!/bin/bash
set -e

if [ "$1" = 'build' ]; then
    ./build.sh
# elif [ "$1" = 'test' ]; then
#     py.test
# elif [ "$1" = 'serve' ]; then
#     supervisord -c /etc/supervisor/supervisord.conf
else
    exec "$@"
fi