'''
This module defines core plot classes for matplotlib visualization.
This is mainly for testing purposes.
'''

import tempfile
import base64
from cStringIO import StringIO
import math

from netCDF4 import Dataset
import numpy as np
from matplotlib import pylab

from ..util.plot import Plot, registerPlotClass


class MplPlot(Plot):
    '''
    Renders a 2D view of a data file using vcs.

    configuration options:

        * int width: The width of the image generated
        * int height: The height of the image generated
        * str filename: The file containing the data
        * str varname: The variable in the file to plot
        * str type: The mpl plot type ('pcolor')
    '''

    #: Default configuration for MplPlot
    _defaults = {
        'width': 640,
        'height': 480,
        'dpi': 150,
        'type': 'pcolor'
    }

    def __init__(self, **kw):
        super(self, MplPlot).__init__(**kw)

    def create(self):
        super(self, MplPlot).create(self)
        # self._canvas = vcs.init()
        self._current['file'] = Dataset(self._current['filename'])

        # setup pylab figure
        pylab.clf()
        self._fig = pylab.figure(
            figsize=(
                int(self._current['width'] / self._current['dpi']),
                int(self._current['height'] / self._current['dpi'])
            )
        )
        self._ax = fig.add_axis([0, 0, 1, 1])

    def value(self, x, y, **kw):
        '''
        Get the value of the data at the given coordinates.
        :param float x: The x-coordinate
        :param float y: The y-coordinate
        :rtype:
        '''
        super(self, MplPlot).value(**kw)

        width = self._current['width']
        height = self._current['height']

        out = None
        if (0 <= x <= width - 1) and (0 <= y <= height - 1):
            imX = math.round(
                self._data.shape[-1] * x / float(width - 1)
            )
            imY = math.round(
                self._data.shape[-2] * (1 - y / float(height - 1))
            )

            out = {
                'value': self._data[imY, imX]
            }

        return out

    def render(self, variable=None, **kw):
        super(self, MplPlot).render(**kw)

        z = kw.get('z', 0)
        t = kw.get('t', 0)

        if not variable:
            variable = self._current('varname', None)

        data = self._file[variable]

        if data.ndim == 3:
            data = data[z, ...].squeeze()
        elif data.ndim == 4:
            data = data[t, z, ...].squeeze()

        self._data = data
        if self._current['type'].lower() == 'pcolor':
            self._ax.imshow(np.flipud(data))

        return self.exportPlot()

    def exportPlot(self):
        '''
        Render the plot to a json string that can be passed over a websocket.
        '''
        self._ax.axis('off')
        im = StringIO()
        self._fig.savefig(
            im,
            format='png',
            transparent=True,
            dpi=self._current['dpi']
        )
        im.seek(0)
        png = base64.base64encode(im.read())
        return {
            'image': png,
            'width': self._current['width'],
            'height': self._current['height']
        }

registerPlotClass('mpl', MplPlot)
