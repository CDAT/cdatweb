'''
This module exposes methods for finding and creating visualizations
compatible with a variable object.
'''

from . import BaseProtocol
from external import exportRpc

from visualizers import __all__ as visualizers

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

        # todo
        return None

    @exportRpc('visualize.server.draw')
    def create(self, fname, varnames, plottype=None, opts={}):
        if plottype is None:
            plottype = 'Isofill'
        f = FileLoader.get_cached_reader(fname)
        var = map(f.read, varnames)

        vis = visualizers[plottype]()
        vis.loadVariable(var, opts)
        vis.render(opts)

        view = vis.getView()
        view.Render()
        id = self.getGlobalId(view)
        self._active[id] = view
        return id

    @exportRpc('visualize.server.render')
    def render_view(self, id):
        view = self._active.get(id)
        if not view:
            return
        view.Render()

    @exportRpc('visualize.server.close')
    def remove_view(self, id):
        view = self._active.pop(id)
        if view:
            view.Finalize()
