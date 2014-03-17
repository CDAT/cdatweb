import types
import sys
import traceback

from paraview.web import protocols as pv_protocols
from autobahn.wamp import exportRpc

#//////////////////////////////////////////////////////////////////////////////
#
# Web protocol for uvis framework
#
#//////////////////////////////////////////////////////////////////////////////
class UVisProtocol(pv_protocols.ParaViewWebProtocol):
    def __init__(self):
        self._plots = {}
        self._nextPlot = -1

    @exportRpc
    def createPlot(self, plotId, *args, **kwargs):
          print "createPlot"
          from plot import PlotFactory
          pl = PlotFactory.createPlot(plotId, *args, **kwargs);
          self._nextPlot += 1
          i = self._nextPlot
          self._plots[i]= pl
          return i

    @exportRpc("stillRender")
    def stillRender(self,options):
        if options['view'] != -1:
            return self._plots[options['view']].render(options);
        else:
            return {};

    @exportRpc("mouseInteraction")
    def mouseInteraction(self, event):
      view = event['view']
      if view != -1:
        return self._plots[view].mouseInteraction(event)