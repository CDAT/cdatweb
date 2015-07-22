'''
This module exposes methods for finding and creating visualizations
compatible with a variable object.
'''

from . import BaseProtocol
from external import exportRpc

import visualizers

from FileLoader import FileLoader


class Visualizer(BaseProtocol):

    _active = {}

    @exportRpc('cdat.view.create')
    def create(self, fname, varnames, plottype=None, opts={}):
        if plottype is None:
            plottype = 'Isofill'

        f = FileLoader().get_reader(fname)
        var = [f[v] for v in varnames]

        vis = visualizers.Isofill()
        vis.loadVariable(var, opts)
        vis.render(opts)

        id = self.getGlobalId(vis.getView())
        self._active[id] = vis
        return id

    @exportRpc('cdat.view.update')
    def render_view(self, id, opts={}):
        return self._active[id].render(opts)

    @exportRpc('cdat.view.destroy')
    def remove_view(self, id):
        view = self._active.pop(id)
        if view:
            view.close()
