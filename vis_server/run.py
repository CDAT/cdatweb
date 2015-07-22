
import sys
import os
import argparse

import vtk

sys.path.append(os.path.dirname(vtk.__file__))  # noqa

from vtk.web import server
from vtk.web import wamp

import vcs

from protocols.VisFinder import Visualizer

from external import exportRpc
import protocols

_viewers = []


class CDATWebVisualizer(wamp.ServerProtocol):

    basePath = '.'
    uploadPath = '.'

    def __init__(self, *arg, **kw):
        wamp.ServerProtocol.__init__(self, *arg, **kw)
        self.traceback_app = True

    def initialize(self):
        # intialize protocols
        self.registerVtkWebProtocol(protocols.MouseHandler())
        self.registerVtkWebProtocol(protocols.ViewPort())
        self.registerVtkWebProtocol(protocols.RemoteRender())
        self.registerVtkWebProtocol(
            protocols.FileBrowser(
                self.uploadPath,
                "Home"
            )
        )
        self.registerVtkWebProtocol(protocols.FileLoader(self.uploadPath))
        self.registerVtkWebProtocol(protocols.FileFinder(self.uploadPath))
        self.registerVtkWebProtocol(protocols.ViewportDeleter())
        self.registerVtkWebProtocol(Visualizer())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='CDATWeb visualization server'
    )

    server.add_arguments(parser)
    args = parser.parse_args()
    CDATWebVisualizer.uploadPath = args.uploadPath

    print("CDATWeb Visualization server initializing")
    server.start_webserver(options=args, protocol=CDATWebVisualizer)
