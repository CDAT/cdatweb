"""This module exposes methods for finding and creating visualizations."""

from . import BaseProtocol
from external import exportRpc

import visualizers

from FileLoader import FileLoader
import vcs


class Visualizer(BaseProtocol):

    _active = {}

    @exportRpc('cdat.vcs.templates')
    def list_templates(self):
        """Return a list of plot templates."""
        return _templates

    @exportRpc('cdat.vcs.methods')
    def list_methods(self):
        """Return a list of plot types and methods."""
        return _methods

    @exportRpc('cdat.view.variable')
    def variable(self, plot, variable):
        """Add or modify the variables used in the plot."""
        if plot not in self._active:
            return False
        all_vars = []
        for obj in variable:
            f = FileLoader().get_reader(obj['file'])
            all_vars.append(
                f[obj['name']]
            )
        return self._active[plot].loadVariable(all_vars)

    @exportRpc('cdat.view.template')
    def template(self, plot, template):
        """Change the given plot's template."""
        if plot in self._active:
            return self._active[plot].setTemplate(template)
        return False

    @exportRpc('cdat.view.create')
    def create(self, plottype, plotmethod, variable, template, opts={}):

        vis = visualizers.VcsPlot()
        vis.setPlotMethod(
            plottype, plotmethod
        )
        vis.setTemplate(template)
        all_vars = []
        for obj in variable:
            f = FileLoader().get_reader(obj['file'])
            var = f[obj['name']]
            if ('subset' in obj):
                kargs = obj['subset']
                print obj['name']
                print kargs
                var = var(**kargs)
            all_vars.append(var)
        vis.loadVariable(all_vars)
        view = vis.getView()
        id = self.getGlobalId(view)
        self._active[id] = vis
        return id

    @exportRpc('cdat.view.update')
    def render_view(self, id, opts={}):
        if id in self._active:
            return self._active[id].render(opts)
        return False

    @exportRpc('cdat.view.destroy')
    def remove_view(self, id):
        view = self._active.pop(id)
        if view:
            view.close()
            return True
        return False

    @classmethod
    def detect_nvars(cls, g_type, g_method, g_obj):
        """Try to return the number of variables required for the plot method.

        Returns the number of variables required by the plot type.
        This isn't really exposed by vcs, so this is written by following this
        insanity:
        https://github.com/UV-CDAT/uvcdat/blob/master/Packages/vcs/Lib/Canvas.py#L251

        The reality is that this api will need to be more complicated in the
        future to account some methods (like meshfill) that can take one or two
        variables depending on the grid.
        """
        g_type = g_type.lower()

        # first check for g_naslabs
        if hasattr(g_obj, 'g_nslabs'):
            return g_obj.g_nslabs

        # then check methods that require 2 variables
        if g_type in _2d_methods:
            return 2

        # meshfill takes one or two, but there are extra requirements that we will
        # have to pass through the api once they are understood
        if g_type == 'meshfill':
            return 1

        # low level primitives should probably not happen
        if g_type in _primitives:
            return 0

        # 1d takes 2 variables
        if g_type == '1d':
            return 2

        # otherwise assume 1
        return 1


# initialize the list of templates and graphics methods
_ = vcs.init()
_templates = sorted(vcs.elements['template'].keys())
_methods = {}
_2d_methods = (
    'scatter', 'vector', 'xvsy', 'stream', 'glyph', '3d_vector', '3d_dual_scalar'
)
_primitives = (
    'line', 'marker', 'fillarea', 'text'
)
for t in vcs.graphicsmethodlist():
    _methods[t] = {}
    for m in vcs.elements[t].keys():
        _methods[t][m] = {
            'nvars': Visualizer.detect_nvars(t, m, vcs.elements[t][m])
        }
