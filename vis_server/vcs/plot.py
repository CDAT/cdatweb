'''
This module defines core plot classes for vcs visualizations.
'''

import vcs
#  import cdms2
#  import MV2

from ..util.plot import Plot, registerPlotClass


#: Default configuration for VcsPlot
_defaults = {
    'width': 640,
    'height': 480,
    'type': 'IsoFill',
    'template': 'default'
}


class VcsPlot(Plot):
    '''
    Renders a 2D view of a data file using vcs.

    configuration options:

        * ...
    '''

    def __init__(self, **kw):
        opts = _defaults.copy()
        opts.update(kw)
        super(self, VcsPlot).__init__(**opts)

    def create(self):
        self._canvas = vcs.init()
        super(self, VcsPlot).create(self)

    def value(self, **kw):
        '''
        '''
        try:  # move to a generic decorator
            pass
        except Exception:
            return None


registerPlotClass('vcs', VcsPlot)
