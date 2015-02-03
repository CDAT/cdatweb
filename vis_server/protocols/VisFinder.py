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

    @exportRpc('visualize.server.plot')
    def create(self, fname, varnames, plottype, opts={}):
        f = FileLoader.get_cached_reader(fname)
        var = map(f.read, varnames)

        vis = visualizers[plottype]()
        vis.loadVariable(var, opts)
        vis.render(opts)
        k = plottype + '_' + fname + '_' + '_'.join(varnames)
        _active[k] = vis

        view = vis.getView()
        view.Render()
        return self.getGlobalId(view)

