
from base import BaseVisualizer

import vcs


class VcsPlot(BaseVisualizer):

    """Base class for all Vcs-based visualization classes."""

    #: vcs plot type
    plot_type = None

    def __init__(self, *arg, **kw):
        super(VcsPlot, self).__init__(*arg, **kw)
        self._canvas = vcs.init()
        self._canvas.setbgoutputdimensions(width=500, height=500, units='pixels')
        self._plot = None

    def render(self, opts={}):
        super(VcsPlot, self).render(opts)

        self._plot = self._canvas.plot(
            self._var[0],
            window_size=(self._width, self._height)
        )

        self._window = self._canvas.backend.renWin
        self._render()
        return True

    def loadVariable(self, var, opts={}):
        """Load a variable into the visualization.

        Returns success or failure.
        """
        self._var = var

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
