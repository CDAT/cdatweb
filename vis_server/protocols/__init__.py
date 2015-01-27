# Modules in this package are protocols available to all applications

# Protocols from vtk proper

# base protocol class
from vtk.web.protocols import vtkWebProtocol as BaseProtocol

# mouse interactor
from vtk.web.protocols import vtkWebMouseHandler as MouseHandler

# basic view port
from vtk.web.protocols import vtkWebViewPort as ViewPort

# server side renderer
from vtk.web.protocols import vtkWebViewPortImageDelivery as RemoteRender

# client side renderer
from vtk.web.protocols import vtkWebViewPortGeometryDelivery as ClientRender

# a basic server side file browser
from vtk.web.protocols import vtkWebFileBrowser as FileBrowser

from .FileLoader import FileLoader
from .FileFinder import FileFinder

from external import exportRpc

class ViewportDeleter(BaseProtocol):
    '''
    Provides a method for deleting a viewport window once the client is done.
    '''

    @exportRpc('cdat.view.destroy')
    def destroy(self, viewId):
        '''
        Delete the viewport corresponding to the given object ID.
        '''
        r = None
        try:
            view = self.getView(viewId)
            view.RemoveAllObservers()
            view.Finalize()
            del view
            print 'Removed view #' + str(viewId)
        except Exception as e:
            r = e
            print e
            print 'Failed to remove view'
        return r

__all__ = [
    BaseProtocol,
    MouseHandler,
    ViewPort,
    RemoteRender,
    ClientRender,
    FileBrowser,
    FileLoader,
    FileFinder,
    ViewportDeleter
]
