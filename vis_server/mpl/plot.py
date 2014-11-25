'''
This module defines core plot classes for matplotlib visualization.
This is mainly for testing purposes.
'''

import json
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
        super(MplPlot, self).__init__(**kw)

    def create(self):
        super(MplPlot, self).create()
        self._current['file'] = self._openFile(self._current['filename'])

        # setup pylab figure
        pylab.clf()
        self._fig = pylab.figure(
            figsize=(
                int(self._current['width'] / self._current['dpi']),
                int(self._current['height'] / self._current['dpi'])
            )
        )
        self._ax = self._fig.add_axes([0, 0, 1, 1])

    def value(self, x, y, **kw):
        '''
        Get the value of the data at the given coordinates.
        :param float x: The x-coordinate
        :param float y: The y-coordinate
        :rtype:
        '''
        super(MplPlot, self).value(**kw)

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

    @classmethod
    def _openFile(cls, filename):
        '''
        Open a file and return the netcdf file object.
        '''
        return Dataset(filename, 'r')

    def render(self, variable=None, **kw):
        super(MplPlot, self).render(**kw)

        z = kw.get('z', 0)
        t = kw.get('t', 0)

        if not variable:
            variable = self._current('varname', None)

        data = self._current['file'][variable]

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
        png = base64.b64encode(im.read())
        return {
            'image': png,
            'width': self._current['width'],
            'height': self._current['height']
        }

registerPlotClass('mpl', MplPlot)


class MplTestPattern(MplPlot):
    '''
    This class is equivalent to :py:class:`MplPlot` except that it generates a
    test pattern rather than opening a physical file.
    '''

    _defaults = MplPlot._defaults.copy()
    _defaults['filename'] = '{}'

    @classmethod
    def _openFile(cls, opts):
        '''
        Generate a test file according to the options given by ``opts``.

        :param str opts: A json string
        :returns: A pseudo-netcdf4 object
        '''

        opts = json.loads(opts)
        default = {
            'A': {
                'shape': [25, 30],
                'values': 1
            },
            'B': {
                'shape': [3, 110, 99],
                'values': [2, 3, 5, 2, 3, 5, 2, 3, 5]
            },
            'C': {
                'shape': [2, 5, 65, 34],
                'values': [2, 3, 5, 7, 11, 1, 13, 19, 17]
            }
        }
        default.update(opts)
        opts = default

        f = {}
        for var in opts:
            v = opts[var]
            a = np.zeros(v['shape'])

            if isinstance(v['values'], (int, float)):
                a[:] = v['values']
            else:
                n = len(a[..., 0, 0].flat)
                for i in xrange(3):
                    ys = math.floor(i / 3.0 * v['shape'][-2])
                    ye = math.ceil((i + 1) / 3.0 * v['shape'][-2])
                    for j in xrange(3):
                        xs = math.floor(j / 3.0 * v['shape'][-1])
                        xe = math.floor((j + 1) / 3.0 * v['shape'][-1])
                        for k in xrange(n):  # This could be vectorized
                            if k == 0:
                                print xs, xe, ys, ye, (v['values'][i * 3 + j] % 11)
                            a[..., ys:ye, xs:xe] = v['values'][i * 3 + j] % 11

            f[var] = a
        return f

registerPlotClass('mpl-test', MplTestPattern)
