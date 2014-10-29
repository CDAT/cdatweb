from vtk.vtkWebCorePython import vtkWebApplication
from vtk.web.protocols import vtkWebMouseHandler, vtkWebViewPortImageDelivery
import os.path, sys, argparse
from PyQt4 import QtCore, QtGui
from packages.CPCViewer.DistributedPointCollections import kill_all_zombies
from packages.CPCViewer.PointCloudViewer import CPCPlot
import multiprocessing
from uvis.plot import Plot

class DV3DPlot(Plot):
    def __init__(self, id="dv3d", type="CPC"):
        super(DV3DPlot, self).__init__(id, type)
        self._grid_file = None
        self._height_varname = None
        self._n_overview_points = 50000000
        self._var_proc_op = None
        self._canvas = None
        self._plotTemplate = "default"
        self._n_cores = multiprocessing.cpu_count()
        self._application = vtkWebApplication()
        self._image_delivery = vtkWebViewPortImageDelivery()
        self._image_delivery.setApplication(self._application)
        self._mouse_handler = vtkWebMouseHandler();
        self._mouse_handler.setApplication(self._application)

    def createContext(self):
      filename = self._data['filename']
      variable = self._data['variable']
      gridfile = self._data.get('gridfile', None)

      try:
        self._plot = CPCPlot( )
        self._plot.init(
          init_args = ( gridfile,
                        filename,
                        variable,
                        self._height_varname,
                        self._var_proc_op ),
                        n_overview_points=self._n_overview_points,
                        n_cores=self._n_cores, show=True )

        self._plot.createConfigDialog(True)
        self._render_window = self._plot.renderWindow
        # Give the render window to the application so it can handle interaction etc.
        self._application.GetObjectIdMap().SetActiveObject("VIEW",
                                                           self._plot.renderWindow)
      except:
        print >> sys.stderr, traceback.format_exc()

    def getValueAt(self, evt):
      pass

    def render(self, options):
      # If we don't have a render window then there is nothing to render
      if not self._render_window:
        return

      # pass the options to VTK
      data = self._image_delivery.stillRender(options)
      data['global_id'] = options['view']
      print "DV3D plot rendering.........................."
      return data


    def mouseInteraction(self, event):
      # If we don't have a render window then just return as not interaction
      # can occur.
      if not self._render_window:
        return

      # pass the event on the vtkWebMouseHandler
      return self._mouse_handler.mouseInteraction(event);

    class Factory:
        def create(self, *args, **kwargs):
            return DV3DPlot(*args, **kwargs)
