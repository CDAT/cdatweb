
from base import BaseVisualizer

import vcs


class VcsPlot(BaseVisualizer):

    """Base class for all Vcs-based visualization classes."""

    #: vcs plot type
    plot_type = None

    @classmethod
    def canView(cls, var):
        try:
            return len(var.info.get('dimensions', [])) >= 2
        except Exception:
            return False

    def __init__(self, *arg, **kw):
        super(VcsPlot, self).__init__(*arg, **kw)
        self._canvas = vcs.init()
        self._plot = None

    def loadVariable(self, var, info, opts={}):
        if len(info['dimensions']) == 4:
            self._var = var
            self._gm = self.plot_type(opts.get('template', 'default'))
        else:
            return False

        for param, value in opts.get('parameters', {}).iteritems():
            self._gm.setParameter(param, value)

        return True

    def render(self, opts={}):
        super(VcsPlot, self).render(opts)

        args = self._var[:]
        args = args + [self._gm]
        self._canvas = vcs.init()
        self._plot = self._canvas.plot(
            *args,
            cdmsfile=self._var.parent.id,
            window_size=(self._width, self._height)
        )

        self._window = self._canvas.backend.plotApps[self._gm].getRenderWindow()
        self._render()
        return True

    def getView(self):
        return self._window


class Isofill(VcsPlot):
    plot_type = vcs.getisofill
    info = dict(VcsPlot.info)
    info['ndims'] = 2
    info['nvars'] = 1


class Volume(VcsPlot):
    plot_type = vcs.get3d_scalar()
    info = dict(VcsPlot.info)
    info['ndims'] = 3
    info['nvars'] = 1
