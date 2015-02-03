
import sys
import os
import argparse

import vtk

sys.path.append(os.path.dirname(vtk.__file__))

from vtk.web import server
from vtk.web import wamp

from external import exportRpc
import settings
_viewers = []

class CDATWebVisualizer(wamp.ServerProtocol):

    authKey = 'secret'
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

    settings.SERVER_TEST=args.testing

    CDATWebVisualizer.authKey = args.authKey
    CDATWebVisualizer.uploadPath = args.uploadPath

import protocols
if not args.testing:
    import vcs
    import cdms2
    class TestProtocol(protocols.BaseProtocol):
        _open_views = {}

        @exportRpc('cdat.view.create')
        def create_view(self, fname, varname, opts={}):
            reader = protocols.FileLoader.get_cached_reader(fname)
            v = reader.read(varname)
            canvas = vcs.init()
            plot = canvas.plot(
                v
            )
            window = canvas.backend.renWin
            window.Render()
            id = self.getGlobalId(window)
            self._open_views[id] = (
                window,
                canvas
            )
            return id

        @exportRpc('cdat.view.destroy')
        def destroy_view(self, id):
            cache = self._open_views.pop(id, None)
            if cache:
                cache[1].close()
                cache[0].Finalize()
else:
    class TestProtocol(protocols.BaseProtocol):
        _open_views = {}

        @exportRpc('cdat.view.create')
        def create_view(self, *arg, **kw):
            renderer = vtk.vtkRenderer()
            renderWindow = vtk.vtkRenderWindow()
            renderWindow.AddRenderer(renderer)

            renderWindowInteractor = vtk.vtkRenderWindowInteractor()
            renderWindowInteractor.SetRenderWindow(renderWindow)
            renderWindowInteractor.GetInteractorStyle().SetCurrentStyleToTrackballCamera()

            cone = vtk.vtkConeSource()
            mapper = vtk.vtkPolyDataMapper()
            actor = vtk.vtkActor()

            mapper.SetInputConnection(cone.GetOutputPort())
            actor.SetMapper(mapper)

            renderer.AddActor(actor)
            renderer.ResetCamera()
            renderWindow.Render()
            id = self.getGlobalId(renderWindow)
            self._open_views[id] = renderWindow
            return id

        @exportRpc('cdat.view.destroy')
        def destroy_view(self, id):
            cache = self._open_views.pop(id, None)
            if cache:
                cache.Finalize()


if __name__ == '__main__':
    print "CDATWeb Visualization server initializing"
    server.start_webserver(options=args, protocol=CDATWebVisualizer)
