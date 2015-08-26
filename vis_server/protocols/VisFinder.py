"""This module exposes methods for finding and creating visualizations."""

from . import BaseProtocol
from external import exportRpc

import visualizers

from FileLoader import FileLoader

import vcs
# initialize the list of templates and graphics methods
_ = vcs.init()
_templates = sorted(vcs.elements['template'].keys())
_methods = sorted(vcs.graphicsmethodlist())


class Visualizer(BaseProtocol):

    _active = {}

    @exportRpc('cdat.view.templates')
    def list_templates(self):
        """Return a list of plot templates."""
        return _templates

    @exportRpc('cdat.view.methods')
    def list_methods(self):
        """Return a list of plot methods."""
        return _methods

    @exportRpc('cdat.view.create')
    def create(self, fname, varnames, plottype='Isofill', opts={}):
        if plottype is None:
            plottype = 'Isofill'

        f = FileLoader().get_reader(fname)
        if isinstance(varnames, basestring):
            varnames = [varnames]
        var = [f[v] for v in varnames]

        vis = getattr(visualizers, plottype)()
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
