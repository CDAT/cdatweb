import sys
import traceback
from PyQt4 import QtCore, QtGui
import tempfile

class PlotFactory(object):
    """
      PlotFactory creates a particular type of plot based on the
      id passed such as VcsPlot.
    """
    _factories = {}

    @staticmethod
    def createPlot(id, *args, **kwargs):
        print "createPlot ........ ", id
        try:
          if not PlotFactory._factories.has_key(id):
              PlotFactory._factories[id] = eval(id + '.Factory()')
          return PlotFactory._factories[id].create(*args, **kwargs)
        except:
          print >> sys.stderr, traceback.format_exc()
class Plot(object):
    """
      Base class for all plots. This class provides the API for plotting
      2D plots which should be implemented by derived classes to provide
      concrete implementation.
    """
    def __init__(self, id=None, config={}):
        self._id = id
        self._data = None
        self._config = config

    def id(self):
        return self._id

    def setId(self, id):
        self._id = id

    def data(self):
        return self._data

    def setData(self, *args, **kwargs):
        self._data = args[0]

    def config(self):
        return self._config

    def setConfig(self, config):
        self._config = config

    def getValueAt(self, evt):
        return {}

    def createContext(self):
        pass

    def render(self, options):
        pass

    def mouseInteraction(self, event):
        pass

    def error(self, message):
        sys.stderr.write("[error]: %s\n" % message)

# Import required modules

# base64 is required to convert image to base64 string
import base64
import datetime

# CDAT
import vcs
import cdms2

import MV2
import json

class VcsPlot(Plot):
    """
      This plot uses VCS for drawing 2D geospatial plots.
    """
    def __init__(self, id="vcs", config={'type':'IsoFill', 'template':'default'}):
        super(VcsPlot, self).__init__(id, config)
        self._file = None
        self._data = {'filename': None, 'variable': None}
        self._canvas = None
        self.image_width = 564.0
        self.image_height = 400.0

    def toJSON(self, imageData, state, mtime, size, format, globalId, localTime, workTime):
        reply = {}
        reply['image'] = imageData
        reply['state'] = state
        reply['mtime'] = mtime
        reply['size'] = size
        reply['format'] = format
        reply['global_id'] = globalId
        reply['localTime'] = localTime
        reply['workTime'] = workTime
        return reply

    def diagRender(self, options):
        """This method may require some testing."""
        filename = self._data['filename']
        variable = self._data['variable']
        self._canvas.clear()
        self._file = cdms2.open(filename)

        varlist = self._file.plot_these
        if isinstance(varlist,list):
            for i in varlist:
                variable = 1
                data = self._file(variable)
                d = self._canvas.plot(data,self.plotTemplate,self._file.presentation,bg=1)
        else:
            variable=varlist
            data = self._file(variable)
            d = self._canvas.plot(data,self._config['template'],self._file.presentation,bg=1)

        png = d._repr_png_()
        f=open("/export/leung25/test.png",'w')
        f.write(png)
        f.close()
        png = base64.b64encode(png)
        return self.toJSON(png, True, datetime.datetime.now().time().microsecond,
                           [self.image_width, self.image_height], "png;base64", options['view'], "", "")

    def createContext(self):
        self._canvas = vcs.init()
        print "createContext", self._canvas

    def getValueAt(self, evt):
        variable = self._data['variable']
        x = evt["x"]
        y = evt["y"]
        cursorX = x / self.image_width
        cursorY = 1.0 - (y / self.image_height)
        v = self._file(variable)
        disp, data = self._canvas.animate_info[0]
        data = data[0]
        t = self._canvas.gettemplate(disp.template)
        dx1 = t.data.x1
        dx2 = t.data.x2
        dy1 = t.data.y1
        dy2 = t.data.y2
        #print "x ", x,cursorX,dx1,dx2
        #print "y ", y, cursorY, dy1,dy2
        if (dx1 < cursorX < dx2) and (dy1 < cursorY < dy2):
            X = data.getAxis(-1)
            Y = data.getAxis(-2)
            if (disp.g_type == "isofill"):
                b = self._canvas.getisofill(disp.g_name)
            if MV2.allclose(b.datawc_x1,1.e20):
                X1 = X[0]
                X2 = X[-1]
            else:
                X1 = b.datawc_x1
                X2 = b.datawc_x2
            if MV2.allclose(b.datawc_y1,1.e20):
                Y1 = Y[0]
                Y2 = Y[-1]
            else:
                Y1 = b.datawc_y1
                Y2 = b.datawc_y2

            L = ((cursorX-dx1)/(dx2-dx1) * (X2-X1)) + X1
            SX = slice(*X.mapInterval((L,L,"cob")))
            l = ((cursorY-dy1)/(dy2-dy1) * (Y2-Y1)) + Y1
            SY = slice(*Y.mapInterval((l,l,"cob")))
            myRank = data.rank()

            if myRank > 2:
                return {'value': str(data[...,SY,SX].flat[0])}
            else:
                return {'value': str(data[...,SY,SX])}
        else:
            return ""

    def render(self, options):
        #self._config['template'] = options.get('template', self._config['template']);
        #self._config['type'] = options.get('type', self._config['type']);
        # self._config['template'] = 'default';
        # self._config['type'] = 'isofill';
        filename = self._data['filename']
        variable = self._data['variable']

        try:
            if (self._canvas is None):
                return self.toJSON(None, True, datetime.datetime.now().time().microsecond,
                               [self.image_width, self.image_height], "png;base64", options['view'], "", "")
            if (filename is None):
                self.error("Invalid filename for the plot")
                return self.toJSON(None, True, datetime.datetime.now().time().microsecond,
                               [self.image_width, self.image_height], "png;base64", options['view'], "", "")

            import os
            if filename == 'test':
                # I have officially given up:
                filename = os.path.abspath(os.path.dirname(__file__) + '/../../../content/data/test.nc')
            self._file = cdms2.open(filename)

            if hasattr(self._file,'presentation'):
                reply = self.diagRender(options)
                return reply

            self._canvas.clear()

            if (variable is None):
                variable = self._file.listvariable()[0]

            data = self._file(variable,slice(0,1))

            # Now plot the canvas
            print data.shape
            print self._config['template']
            print self._config['type'].lower()
            if self._config["type"].lower()=="isofill":
                g = self._canvas.createisofill()

            d = self._canvas.plot(data,g, bg=1)
            print "done plotting"
            pngfile = tempfile.NamedTemporaryFile(suffix='.png')
            self._canvas.png(pngfile.name)
            png = open(pngfile.name, 'r').read()
            png = base64.b64encode(png)

            return self.toJSON(png, True, datetime.datetime.now().time().microsecond,
                               [self.image_width, self.image_height], "png;base64", options['view'], "", "")

        except Exception as e:
            print e

        return {}

    class Factory:
        def create(self, *args, **kwargs):
            return VcsPlot(*args, **kwargs)


import os.path, sys, argparse
import vtk

# necessary because reasons:
sys.path.append(os.path.dirname(vtk.__file__))

from vtk.vtkWebCorePython import vtkWebApplication
from vtk.web.protocols import vtkWebMouseHandler, vtkWebViewPortImageDelivery
from PyQt4 import QtCore, QtGui
from packages.CPCViewer.DistributedPointCollections import kill_all_zombies
from packages.CPCViewer.PointCloudViewer import CPCPlot
import multiprocessing

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
        self._mouse_handler = vtkWebMouseHandler()
        self._mouse_handler.setApplication(self._application)
        self._render_window = True

    def createContext(self):
      return
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
