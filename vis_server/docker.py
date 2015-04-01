#!/usr/bin/env python
"""This script starts up visualization server from docker."""

import time
import os
import sys
import subprocess
from random import choice
import string

this_dir = os.path.abspath(os.path.dirname(__file__))
background = []
name = ''.join(choice(string.ascii_uppercase + string.digits) for _ in range(6))
dockercmd = " ".join([
    "docker run --name={} --rm=true -p {}:{} -t uvcdat/cdatweb-vtkweb",
    "python", "/opt/cdatweb/run.py", "--port", "{}", "--upload-directory", "/data"
])

def main_linux(port):
    """Start a vis server from a linux host on the given port."""
    subprocess.check_call(
        dockercmd.format(name, port, port, port),
        shell=True
    )


def main_osx(port):
    """Start a vis server and port forward into the docker vm."""
    proc = subprocess.Popen(
        "boot2docker ssh -L {}:localhost:{} -N".format(port, port),
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(0.5)
    if proc.poll() is not None:
        raise Exception("Could not create tunnel from port {}.".format(port))

    background.append(proc)
    subprocess.check_call(
        "$(boot2docker shellinit); " + dockercmd.format(name, port, port, port),
        shell=True
    )


def cleanup():
    """Stop in ongoing processes."""
    for proc in background:
        proc.terminate()
    subprocess.call(
        "$(boot2docker shellinit 2> /dev/null); docker kill {}".format(name),
        shell=True
    )

if __name__ == '__main__':
    try:
        port = 7000
        if len(sys.argv) > 1:
            port = int(sys.argv[1])

        if sys.platform.startswith('linux'):
            main_linux(port)
        elif sys.platform == 'darwin':
            main_osx(port)
        else:
            print('Unsupported platform')
    finally:
        print('called cleanup')
        cleanup()
