#!/bin/bash

# Starts up the twisted application to serve the visualization backend.

pth=$(dirname $0)

source ${pth}/environ.sh

python ${script} --port ${SOCKETPORT:-8080} --content ${common_content} --app-content ${app_content} "$@"
