
import sys
import os
import argparse

import vtk

sys.path.append(os.path.dirname(vtk.__file__))

from vtk.web import server
from vtk.web import wamp

import protocols
from external import exportRpc


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

class TestProtocol(protocols.BaseProtocol):

    @exportRpc('cdat.view.create')
    def create_view(self):
        # just for testing:
        # VTK specific code
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

        # self.Application.GetObjectIdMap().SetActiveObject("VIEW", renderWindow)
        return self.getGlobalId(renderWindow)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='CDATWeb visualization server'
    )

    server.add_arguments(parser)

    # Add local options here:

    args = parser.parse_args()

    CDATWebVisualizer.authKey = args.authKey
    CDATWebVisualizer.uploadPath = args.uploadPath

    print "CDATWeb Visualization server initializing"
    server.start_webserver(options=args, protocol=CDATWebVisualizer)
