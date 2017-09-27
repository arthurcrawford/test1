#!/bin/bash
sudo docker build -t com.a4pizza.raptly.itest src/itest
sudo docker rm -f com.a4pizza.raptly.itest >&/dev/null
sudo docker run --rm -d -p 9876:8080 --name com.a4pizza.raptly.itest com.a4pizza.raptly.itest serve
while ! curl -s http://localhost:9876/api/version | grep Version; do
  sleep 0.1 # wait for 1/10 of the second before check again
done
PYTHONPATH=src/main/python pytest src/itest/python
