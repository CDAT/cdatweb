'''
This module exposes methods for finding and creating visualizations
compatible with a variable object.
'''

from . import BaseProtocol
from external import exportRpc

from visualizers import __all__ as visualizers


class Visualizer(BaseProtocol):

    @exportRpc('visualize.server.list')
    def list(self, file_info=None):
        '''
        List all visualizers capable of openinng the given file.
        If no file is provided, then list all visualizers.
        '''
        if file_info is None:
            return visualizers[:]

        return map
