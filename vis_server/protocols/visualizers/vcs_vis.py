import datetime
import base64

from base import BaseVisualizer
from plotter import PlotManager

import vcs


class VcsPlot(BaseVisualizer):

    """Base class for all Vcs-based visualization classes."""

    #: vcs plot type
    plot_type = None

    def __init__(self, *arg, **kw):
        super(VcsPlot, self).__init__(*arg, **kw)
        self._window = None
        self._canvas = vcs.init()
        self._plot = PlotManager(self._canvas)
        self._plot.graphics_method = vcs.getisofill() # default
        self._plot.template = vcs.elements['template']['default'] # default

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

    def render(self, cfg):
        # call the super method to set the requested image size
        super(VcsPlot, self).render(cfg)

        self.getView().SetSize(self._width, self._height)
        # self._canvas.update()
        self._canvas.setbgoutputdimensions(self._width, self._height, units="pixels")
        d = self._plot.plot()
        png = d._repr_png()
        png = base64.b64encode(png)

        return self.toJSON(png, True, datetime.datetime.now().time().microsecond,
                           [self._width, self._height], "png;base64", cfg['view'], "", "")

    def setPlotMethod(self, plot_type, plot_method):
        method = vcs.getgraphicsmethod(plot_type, plot_method)
        if method:
            self._plot.graphics_method = method
            return True
        else:
            return False

    def setTemplate(self, template):
        if template in vcs.elements['template']:
            self._plot.template = vcs.elements['template'][template]
            return True
        else:
            return False

    def loadVariable(self, var, opts={}):
        """Load a variable into the visualization.

        Returns success or failure.
        """
        self._plot.variables = var
        return True

    def getView(self):
        return self._canvas.backend.renWin
