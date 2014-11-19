#!/usr/bin/env python

import os
import sys
import vtk

sys.path.append(os.path.dirname(vtk.__file__))

from vtk.web import server, wamp, protocols


class VTKWebApp(wamp.ServerProtocol):

    _view = None
    _renderer = None

    def __init__(self, *arg, **kw):
        wamp.ServerProtocol.__init__(self, *arg, **kw)

    @classmethod
    def _createView(cls):
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

        cls._renderer = renderer
        cls._view = renderWindow

    @classmethod
    def _renderActiveView(cls):
        cls._renderer.ResetCamera()
        cls._view.Render()

    def initialize(self):
        wamp.ServerProtocol.initialize(self)

        self.registerVtkWebProtocol(protocols.vtkWebMouseHandler())
        self.registerVtkWebProtocol(protocols.vtkWebViewPort())
        self.registerVtkWebProtocol(protocols.vtkWebViewPortImageDelivery())
        self.registerVtkWebProtocol(protocols.vtkWebViewPortGeometryDelivery())

        if not self._view:
            self._createView()
            self.addActors(self._renderer, self._view)
            self._renderActiveView()

        self.Application.GetObjectIdMap().SetActiveObject('VIEW', self._view)

if __name__ == '__main__':

    from test_apps import get_apps
    import sys

    apps = get_apps(VTKWebApp)

    # parse arguments (probably use server.start_webserver instead)
    arg = 'cube'
    if len(sys.argv) > 1 and sys.argv[-1] in apps or sys.argv[-1] == 'list':
        arg = sys.argv.pop()

    if arg == 'list':
        h = []
        h.append("Valid applications:")
        for k in apps:
            h.append("  " + k)

        print >> sys.stderr, '\n'.join(h)
        sys.exit(0)
    else:
        print 'Starting application: "%s"' % arg
        server.start(protocol=apps[arg])
