import sys
import traceback

import rpc

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
              raise RuntimeError("Unable to create plot of type %s\n" % id)

          return PlotFactory._factories[id](*args, **kwargs)
        except:
          print >> sys.stderr, traceback.format_exc()
          raise

    @staticmethod
    def registerFactory(name, factory):
        PlotFactory._factories[name] = factory

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

    @rpc.export
    def id(self):
        return self._id

    @rpc.export
    def setId(self, id):
        self._id = id

    @rpc.export
    def data(self):
        return self._data

    @rpc.export
    def setData(self, *args, **kwargs):
        self._data = args[0]

    @rpc.export
    def config(self):
        return self._config

    @rpc.export
    def setConfig(self, config):
        self._config = config

    @rpc.export
    def getValueAt(self, evt):
        return {}

    @rpc.export
    def createContext(self):
        pass

    @rpc.export
    def render(self, options):
        pass

    @rpc.export
    def mouseInteraction(self, event):
        pass

    @rpc.export
    def error(self, message):
        sys.stderr.write("[error]: %s\n" % message)
