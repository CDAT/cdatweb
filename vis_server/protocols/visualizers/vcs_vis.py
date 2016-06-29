
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
        self._plot.graphics_method = vcs.getisofill()              # default
        self._plot.template = vcs.elements['template']['default']  # default

    def render(self, opts={}):
        super(VcsPlot, self).render(opts)

        self._window = self.getView()

        if not self._window:
            return
        self._window.SetSize(self._width, self._height)
        self._canvas.backend.configureEvent(None, None)
        self._canvas.update()
        return True

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
