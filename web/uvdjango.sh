#!/bin/bash

# Starts up the django application to serve the front end content.

pth=$(dirname $0)

source ${pth}/environ.sh

python ${django_script} runserver 0.0.0.0:${WEBPORT:-8000}
