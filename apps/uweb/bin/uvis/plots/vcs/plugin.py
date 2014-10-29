# base64 is required to convert image to base64 string
import base64
import datetime

# CDAT
# Import vcs from the uvis package to resolve with vcs module we are refering
# to. We can simply import vcs as we are in a module called vcs.
from uvis import vcs
import cdms2

import MV2
import json
from uvis.plot import Plot

class VcsPlot(Plot):
    """
      This plot uses VCS for drawing 2D geospatial plots.
    """
    def __init__(self, id="vcs", config={'type':'IsoFill', 'template':'default'}):
        super(VcsPlot, self).__init__(id, config)
        self._file = None
        self._data = {'filename': None, 'variable': None}
        self._canvas = None
        self.image_width = 564.0
        self.image_height = 400.0

    def toJSON(self, imageData, state, mtime, size, format, globalId, localTime, workTime):
        reply = {}
        reply['image'] = imageData
        reply['state'] = state
        reply['mtime'] = mtime
        reply['size'] = size
        reply['format'] = format
        reply['global_id'] = globalId
        reply['localTime'] = localTime
        reply['workTime'] = workTime
        return reply

    def diagRender(self, options):
        """This method may require some testing."""
        filename = self._data['filename']
        variable = self._data['variable']
        self._canvas.clear()
        self._file = cdms2.open(filename)

        varlist = self._file.plot_these
        if isinstance(varlist,list):
            for i in varlist:
                variable = 1
                data = self._file(variable)
                d = self._canvas.plot(data,self.plotTemplate,self._file.presentation,bg=1)
        else:
            variable=varlist
            data = self._file(variable)
            d = self._canvas.plot(data,self._config['template'],self._file.presentation,bg=1)

        png = d._repr_png_()
        f=open("/export/leung25/test.png",'w')
        f.write(png)
        f.close()
        png = base64.b64encode(png)
        return self.toJSON(png, True, datetime.datetime.now().time().microsecond,
                           [self.image_width, self.image_height], "png;base64", options['view'], "", "")

    def createContext(self):
        self._canvas = vcs.init()
        print "createContext", self._canvas

    def getValueAt(self, evt):
        variable = self._data['variable']
        x = evt["x"]
        y = evt["y"]
        cursorX = x / self.image_width
        cursorY = 1.0 - (y / self.image_height)
        v = self._file(variable)
        disp, data = self._canvas.animate_info[0]
        data = data[0]
        t = self._canvas.gettemplate(disp.template)
        dx1 = t.data.x1
        dx2 = t.data.x2
        dy1 = t.data.y1
        dy2 = t.data.y2
        #print "x ", x,cursorX,dx1,dx2
        #print "y ", y, cursorY, dy1,dy2
        if (dx1 < cursorX < dx2) and (dy1 < cursorY < dy2):
            X = data.getAxis(-1)
            Y = data.getAxis(-2)
            if (disp.g_type == "isofill"):
                b = self._canvas.getisofill(disp.g_name)
            if MV2.allclose(b.datawc_x1,1.e20):
                X1 = X[0]
                X2 = X[-1]
            else:
                X1 = b.datawc_x1
                X2 = b.datawc_x2
            if MV2.allclose(b.datawc_y1,1.e20):
                Y1 = Y[0]
                Y2 = Y[-1]
            else:
                Y1 = b.datawc_y1
                Y2 = b.datawc_y2

            L = ((cursorX-dx1)/(dx2-dx1) * (X2-X1)) + X1
            SX = slice(*X.mapInterval((L,L,"cob")))
            l = ((cursorY-dy1)/(dy2-dy1) * (Y2-Y1)) + Y1
            SY = slice(*Y.mapInterval((l,l,"cob")))
            myRank = data.rank()

            if myRank > 2:
                return {'value': str(data[...,SY,SX].flat[0])}
            else:
                return {'value': str(data[...,SY,SX])}
        else:
            return ""

    def render(self, options):
        #self._config['template'] = options.get('template', self._config['template']);
        #self._config['type'] = options.get('type', self._config['type']);
        # self._config['template'] = 'default';
        # self._config['type'] = 'isofill';
        filename = self._data['filename']
        variable = self._data['variable']
        try:
            if (self._canvas is None):
                return self.toJSON(None, True, datetime.datetime.now().time().microsecond,
                               [self.image_width, self.image_height], "png;base64", options['view'], "", "")
            if (filename is None):
                self.error("Invalid filename for the plot")
                return self.toJSON(None, True, datetime.datetime.now().time().microsecond,
                               [self.image_width, self.image_height], "png;base64", options['view'], "", "")

            self._file = cdms2.open(filename)

            if hasattr(self._file,'presentation'):
                reply = self.diagRender(options)
                return reply

            self._canvas.clear()

            if (variable is None):
                variable = self._file.listvariable()[0]

            data = self._file(variable,slice(0,1))

            # Now plot the canvas
            print data.shape
            print self._config['template']
            print self._config['type'].lower()
            if self._config["type"].lower()=="isofill":
                g = self._canvas.createisofill()

            d = self._canvas.plot(data,g, bg=1)
            print "done plotting"
            png = d._repr_png_()
            png = base64.b64encode(png)

            return self.toJSON(png, True, datetime.datetime.now().time().microsecond,
                               [self.image_width, self.image_height], "png;base64", options['view'], "", "")

        except Exception as e:
            print e

        return {}

    class Factory:
        def create(self, *args, **kwargs):
            return VcsPlot(*args, **kwargs)
