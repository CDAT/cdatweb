
import vtk


def ApplicationFactory(VTKWebApp):

    class Cone(VTKWebApp):

        def initialize(self):

            VTKWebApp.initialize(self)

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

            self.view = renderWindow
            self.Application.GetObjectIdMap().SetActiveObject('VIEW', renderWindow)

    return Cone
