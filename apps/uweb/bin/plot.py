
class PlotFactory(object):
    _factories = {}

    @staticmethod
    def createPlot(id, *args, **kwargs):
        if not PlotFactory._factories.has_key(id):
            PlotFactory._factories[id] = eval(id + '.Factory()')
        return PlotFactory._factories[id].create(*args, **kwargs)

class Plot(object):
    def __init__(self, id=None, type=None):
        self._id = id
        self._type = type
        self._sources = None
        self._variables = None

    def id(self):
        return self._id

    def setId(self, id):
        self._id = id

    def sources(self):
        return self._sources

    def setSources(self, sources):
        print 'calling setSources'
        self._sources = sources

    def variables(self):
        return self._variables

    def setVariables(self, variables):
        self._variables = variables

    def createContext(self):
        pass

    def render(self, options):
        pass

    def error(self, message):
        sys.stderr.write("[error]: %s\n" % message)

# Import required modules

# base64 is required to convert image to base64 string
import base64
import datetime

# CDAT
import vcs
import cdms2

class VcsPlot(Plot):
    def __init__(self, id="vcs", type="BoxFill"):
        super(VcsPlot, self).__init__(id, type)
        self._canvas = None
        self._plotTemplate= "default"

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

    def diagRender(self):
        pass

    def createContext(self):
        self._canvas = vcs.init()

    def render(self, options):
        print 'calling render on the plot 1'
        try:
            if (self._sources is None):
              self.error("Invalid sources for the plot")
              return

            # vcs plot can handle only one source
            source = self._sources[0];

            print 'calling render on the plot 2'

            self.f = cdms2.open(source)
            if hasattr(self.f,'presentation'):
                reply = self.diagRender()
                return reply

            self._canvas.clear()

            if (self._variables is None or len(self._variables) == 0):
              self._variables = self.f.listvariable()

            # use the first variable to plot the data
            variable = self._variables[0]

            data = self.f(variable)

            # Now plot the canvas
            d = self._canvas.plot(data, self._plotTemplate, self._type, bg=1)

            png = d._repr_png_()
            png = base64.b64encode(png)

            print 'calling render on the plot 3'

            return self.toJSON(png, True, datetime.datetime.now().time().microsecond,
                               [550, 400], "png;base64", "", "", "")

        except Exception as e:
            print e

        return {}

    class Factory:
        def create(self, *args, **kwargs):
            return VcsPlot(*args, **kwargs)
