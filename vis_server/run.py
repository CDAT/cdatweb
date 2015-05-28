#!/usr/bin/env python

import sys
import os
import argparse

import vtk

sys.path.append(os.path.dirname(vtk.__file__))  # noqa

from vtk.web import server
from vtk.web import wamp

import protocols
from protocols.readers import cdms_reader
import vcs

from external import exportRpc
import settings
_viewers = []


class CDATWebVisualizer(wamp.ServerProtocol):

    basePath = '.'
    uploadPath = '.'

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
        self.registerVtkWebProtocol(TestProtocol())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='CDATWeb visualization server'
    )

    server.add_arguments(parser)
    parser.add_argument(
        '--testing',
        action='store_true',
        dest='testing',
        help='Enable testing mode (bypass uvcdat)'
    )

    args = parser.parse_args()

    settings.SERVER_TEST = args.testing

    CDATWebVisualizer.uploadPath = args.uploadPath


class TestProtocol(protocols.BaseProtocol):
    _open_views = {}
    _dirty_views = {}

    @exportRpc('cdat.view.create')
    def create_view(self, fname, varname, opts={}):
        reader = cdms_reader.Cdms_reader(fname)
        v = reader.read(varname)
        canvas = vcs.init()
        canvas.setbgoutputdimensions(width=500, height=500, units='pixels')
        canvas.plot(v)
        window = canvas.backend.renWin
        id = self.getGlobalId(window)
        self._open_views[id] = (
            window,
            canvas
        )

        def dirty(*arg, **kw):
            self._dirty_views[id] = True

        def resize(*arg, **kw):
            if self._dirty_views.pop(id, None):
                canvas.update()

        window.AddObserver(vtk.vtkCommand.ModifiedEvent, dirty)
        window.AddObserver(vtk.vtkCommand.EndEvent, resize)

        return id

    @exportRpc('cdat.view.update')
    def update_view(self, id):
        window, canvas = self._open_views[id]
        canvas.update()
        window.Render()

    @exportRpc('cdat.view.destroy')
    def destroy_view(self, id):
        cache = self._open_views.pop(id, None)
        if cache:
            cache[1].close()
            cache[0].Finalize()

if __name__ == '__main__':
    print("CDATWeb Visualization server initializing")
    server.start_webserver(options=args, protocol=CDATWebVisualizer)
