
import sys
import os
import argparse

import vtk

sys.path.append(os.path.dirname(vtk.__file__))

from vtk.web import server
from vtk.web import wamp

from util.settings import DATA_DIRECTORY
import protocols


class CDATWebVisualizer(wamp.ServerProtocol):

    authKey = 'secret'
    basePath = '.'

    def initialize(self):
        # intialize protocols
        self.registerVtkWebProtocol(protocols.MouseHandler())
        self.registerVtkWebProtocol(protocols.ViewPort())
        self.registerVtkWebProtocol(protocols.RemoteRender())
        self.registerVtkWebProtocol(
            protocols.FileBrowser(DATA_DIRECTORY, "Home")
        )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='CDATWeb visualization server'
    )

    server.add_arguments(parser)

    # Add local options here:

    args = parser.parse_args()

    CDATWebVisualizer.authKey = args.authKey
    CDATWebVisualizer.authKey = args.uploadPath

    print "CDATWeb Visualization server initializing"
    server.start_webserver(options=args, protocol=CDATWebVisualizer)
