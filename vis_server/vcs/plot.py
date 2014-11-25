'''
This module defines core plot classes for vcs visualizations.
'''

import tempfile
import base64

import vcs
import cdms2
import MV2

from ..util.plot import Plot, registerPlotClass


class VcsPlot(Plot):
    '''
    Renders a 2D view of a data file using vcs.

    configuration options:

        * int width: The width of the image generated
        * int height: The height of the image generated
        * str filename: The file containing the data
        * str varname: The variable in the file to plot
        * str type: The vcs plot type
        * str template: ?
    '''

    #: Default configuration for VcsPlot
    _defaults = {
        'width': 640,
        'height': 480,
        'type': 'IsoFill',
        'template': 'default'
    }

    def __init__(self, **kw):
        super(VcsPlot, self).__init__(**kw)

    def create(self):
        super(VcsPlot, self).create()
        self._canvas = vcs.init()
        self._current['file'] = cdms2.open(self._current['filename'])

    def value(self, x, y, **kw):
        '''
        Get the value of the data at the given coordinates.
        :param float x: The x-coordinate
        :param float y: The y-coordinate
        :rtype:
        '''
        super(VcsPlot, self).value(**kw)

        width = self._current['width']
        height = self._current['height']

        cursorX = x / float(width)
        cursorY = 1 - y / float(height)

        # in the original code for some reason:
        # var = self._current['file'](self._current['varname'])

        disp, data = self._canvas.animate_info[0]
        data = data[0]

        template = self._canvas.gettemplate(disp.template)

        dx1 = template.data.x1
        dx2 = template.data.x2
        dy1 = template.data.y1
        dy2 = template.data.y2

        output = None
        if (dx1 < cursorX < dx2) and (dy1 < cursorY < dy2):

            X = data.getAxis(-1)
            Y = data.getAxis(-2)

            # The rest, ¯\(°_o)/¯
            if (dx1 < cursorX < dx2) and (dy1 < cursorY < dy2):
                X = data.getAxis(-1)
                Y = data.getAxis(-2)
                if (disp.g_type == "isofill"):
                    b = self._canvas.getisofill(disp.g_name)
                if MV2.allclose(b.datawc_x1, 1.e20):
                    X1 = X[0]
                    X2 = X[-1]
                else:
                    X1 = b.datawc_x1
                    X2 = b.datawc_x2
                if MV2.allclose(b.datawc_y1, 1.e20):
                    Y1 = Y[0]
                    Y2 = Y[-1]
                else:
                    Y1 = b.datawc_y1
                    Y2 = b.datawc_y2

                L = ((cursorX-dx1)/(dx2-dx1) * (X2-X1)) + X1
                SX = slice(*X.mapInterval((L, L, "cob")))
                l = ((cursorY-dy1)/(dy2-dy1) * (Y2-Y1)) + Y1
                SY = slice(*Y.mapInterval((l, l, "cob")))
                myRank = data.rank()

                if myRank > 2:
                    return {'value': str(data[..., SY, SX].flat[0])}
                else:
                    return {'value': str(data[..., SY, SX])}

        return output

    def render(self, variable=None, **kw):
        super(VcsPlot, self).render(**kw)
        if not variable:
            variable = self._current('varname', None)
        if not variable:
            # probably a bad idea:
            variable = self._file.listvariable()[0]

        data = self._file(variable, slice(0, 1))
        self._canvas.clear()

        if self._current['type'].lower() == 'isofill':
            g = self._canvas.createisofill()

        self._canvas.plot(data, g, bg=1)
        pngfile = tempfile.NamedTemporaryFile(suffix='.png')
        self._canvas.png(pngfile.name)
        return self.exportPlot(pngfile)

    def exportPlot(self, pngfile):
        '''
        Render the plot to a json string that can be passed over a websocket.
        '''
        png = base64.base64encode(open(pngfile.name, 'r').read())
        return {
            'image': png,
            'width': self._current['width'],
            'height': self._current['height']
        }

registerPlotClass('vcs', VcsPlot)
