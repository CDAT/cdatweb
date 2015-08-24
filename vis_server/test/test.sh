#!/bin/bash
arg=$1
echo $arg
if [[ $arg == "basic" ]] ; then
    echo "Starting loop"
elif [[ $arg == "fail" ]] ; then
    echo "die"
    exit 1
elif [[ $arg == "timeout" ]] ; then
    sleep 60
    echo "Starting loop"
    sleep 30
    exit 1
else
    echo "unknown test method"
    exit 2
fi
while true ; do
    date
    sleep 10
done
