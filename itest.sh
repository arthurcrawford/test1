#!/bin/bash

docker build --build-arg APTLY_VERSION_ARG=${APTLY_VERSION:-1.2.0} --force-rm -t com.a4pizza.raptly.itest src/itest
docker rm -f com.a4pizza.raptly.itest >&/dev/null
docker run --rm -d -p 9876:8080 -p9877:8000 --name com.a4pizza.raptly.itest com.a4pizza.raptly.itest serve

# Wait in 1/10 second intervals for the aptly API to become available
while ! curl -s http://localhost:9876/api/version | grep Version; do
  sleep 0.1
done
PYTHONPATH=src/main/python pytest src/itest/python
