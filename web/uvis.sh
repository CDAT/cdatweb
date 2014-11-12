#!/bin/bash

pth=$(dirname $0)

exec $pth/socket.sh "$@" &> socket.log &
exec $pth/uvdjango.sh &> uvdjango.log &
