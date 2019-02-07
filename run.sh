#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
docker build -f docker/Dockerfile.ri-test-tool -t ri-test-tool .
docker run  -v "$SCRIPT_DIR":/home/run -p 8888:8888  ri-test-tool
