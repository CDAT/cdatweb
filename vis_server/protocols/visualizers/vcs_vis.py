
from base import BaseVisualizer
from plotter import PlotManager

import vcs


class VcsPlot(BaseVisualizer):

    """Base class for all Vcs-based visualization classes."""

    #: vcs plot type
    plot_type = None

    def __init__(self, *arg, **kw):
        super(VcsPlot, self).__init__(*arg, **kw)
        self._canvas = vcs.init()
        self._plot = PlotManager(self._canvas)
        self._plot.graphics_method = self.plot_type
        self._plot.template = vcs.elements['template']['default']

    def render(self, opts={}):
        super(VcsPlot, self).render(opts)

        self._window = self._canvas.backend.renWin

        if not self._window:
            return
        self._window.SetSize(self._width, self._height)
        self._canvas.backend.configureEvent(None, None)
        self._canvas.update()
        return True

    def loadVariable(self, var, opts={}):
        """Load a variable into the visualization.

        Returns success or failure.
        """
        self._plot.variables = var

    def getView(self):
        return self._window


class Isofill(VcsPlot):
    plot_type = vcs.getisofill()
    info = dict(VcsPlot.info)
    info['ndims'] = 2
    info['nvars'] = 1


class Volume(VcsPlot):
    plot_type = vcs.get3d_scalar()
    info = dict(VcsPlot.info)
    info['ndims'] = 3
    info['nvars'] = 1


class Vector2D(VcsPlot):
    plot_type = vcs.getvector()
    info = dict(VcsPlot.info)
    info['ndims'] = 2
    info['nvars'] = 2


class Vector3D(VcsPlot):
    plot_type = vcs.get3d_vector()
    info = dict(VcsPlot.info)
    info['ndims'] = 3
    info['nvars'] = 2  # http://uvcdat.llnl.gov/documentation/vcs/vcs-8.html#vcs3D_vector
