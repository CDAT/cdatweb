
from base import BaseVisualizer

import vcs


# TODO: make individual subclasses out of different vcs plot types
class Vcs_plot(BaseVisualizer):

    @classmethod
    def canView(cls, var, info):
        return len(info['dimensions']) == 4

    def __init__(self, *arg, **kw):
        super(Vcs_plot, self).__init__(*arg, **kw)
        self._canvas = vcs.init()

    def loadVariable(self, var, info, opts={}):
        if len(info['dimensions']) == 4:
            self._var = var
            self._gm = vcs.get3d_scalar('default')
        else:
            return False

        for param, value in opts.get('parameters', {}).iteritems():
            self._gm.setParameter(param, value)

        return True

    def render(self, opts={}):
        super(Vcs_plot, self).render(opts)

        self._plot = self._canvas.plot(
            self._var,
            self._gm,
            cdmsfile=self._var.parent.id,
            window_size=(self._width, self._height)
        )

        self._window = self.canvas.backend.plotApps[self._gm].getRenderWindow()
        return True

    def getView(self):
        return self._window
