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

    @exportRpc('visualize.server.list')
    def list(self, file_info=None):
        '''
        List all visualizers capable of openinng the given file.
        If no file is provided, then list all visualizers.
        '''
        if file_info is None:
            return visualizers.keys()

        # todo list valid plot types for the give file
        return None

    @exportRpc('visualize.server.plot')
    def create(self, fname, varnames, plottype=None, opts={}):
        if plottype is None:
            plottype = 'Isofill'
        f = FileLoader().get_reader(fname)
        var = map(f.read, varnames)

        vis = getattr(visualizers, plottype)()
        vis.loadVariable(var, opts)
        vis.render(opts)

        id = self.getViewId()
        self._active[id] = vis
        return id

    @exportRpc('visualize.server.render')
    def render_view(self, id, opts={}):
        return self._active[id].render(opts)

    @exportRpc('visualize.server.close')
    def remove_view(self, id):
        view = self._active.pop(id)
        if view:
            view.close()
