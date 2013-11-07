"""
    This module is a ParaViewWeb server application.
    The following command line illustrate how to use it::

        $ pvpython hello.py --file <filename>
                            --ds-host <hostname>
                            --ds-port <port>
                            --rs-host <hostname>
                            --rs-port <port>

        --ds-host None
             Host name where pvserver has been started

        --ds-port 11111
              Port number to use to connect to pvserver

        --rs-host None
              Host name where renderserver has been started

        --rs-port 22222
              Port number to use to connect to the renderserver

    Any ParaViewWeb executable script come with a set of standard arguments that
    can be overriden if need be::

        --port 8080
             Port number on which the HTTP server will listen to.

        --content /path-to-web-content/
             Directory that you want to server as static web content.
             By default, this variable is empty which mean that we rely on another server
             to deliver the static content and the current process only focus on the
             WebSocket connectivity of clients.

        --authKey vtkweb-secret
             Secret key that should be provided by the client to allow it to make any
             WebSocket communication. The client will assume if none is given that the
             server expect "vtkweb-secret" as secret key.

"""

# import to process args
import os
import sys
import base64
import vcs
import cdms2
import MV2

# import paraview modules.
from vtk.web import wamp
from paraview.web import wamp      as pv_wamp
from paraview.web import protocols as pv_protocols

from vtk.web import server

try:
    import argparse
except ImportError:
    # since  Python 2.6 and earlier don't have argparse, we simply provide
    # the source for the same as _argparse and we use it instead.
    import _argparse as argparse


from autobahn.wamp import exportRpc

class UWebProtocol(pv_protocols.ParaViewWebProtocol):

    def __init__(self):
        self._netcdfFile = None
        self._initRender = False
        self._plotType = None
        self._plotTemplate= "default"
        self._canvas = vcs.init()
        self._viewSelection = None
        self._variable = None
        self.f = None
        self.image_width=864.0
        self.image_height=646.0

    def setFileName(self, filename):
        self._netcdfFile = filename

    @exportRpc("mouseInteraction")
    def mouseInteraction(self, event):
        print "mouseInteraction ..."
        x=event["x"]
        y=event["y"]
        x_percent=x/self.image_width
        y_percent=1.0-(y/self.image_height)

        data=self.getDataValueFromCursor(x_percent,y_percent)
        data=str(data)
        print x,y, x_percent,y_percent,data
        return data

    @exportRpc("getDataValueFromCursor")
    def getDataValueFromCursor(self, cursorX, cursorY):
        #f=cdms2.open(self._netcdfFile)
        v=self.f(self._variable)
        disp, data = self._canvas.animate_info[0]
        data = data[0]
        t=self._canvas.gettemplate(disp.template)
        dx1 = t.data.x1
        dx2 = t.data.x2
        dy1 = t.data.y1
        dy2 = t.data.y2
        print "cursorX: ", cursorX
        print "cursorY: ", cursorY
        print "dx1", dx1
        print "dx2", dx2
        print "dy1", dy1
        print "dy2",  dy2
        if (dx1 < cursorX < dx2) and (dy1 < cursorY < dy2):
            X = data.getAxis(-1)
            Y = data.getAxis(-2)
            if (disp.g_type == "boxfill"):
                b = self._canvas.getboxfill(disp.g_name)
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
            print "X1", X1
            print "X2", X2
            print "Y1", Y1
            print "Y2", Y2

            L = ((cursorX-dx1)/(dx2-dx1)*(X2-X1))+X1
            SX = slice(*X.mapInterval((L,L,"cob")))
            l = ((cursorY-dy1)/(dy2-dy1)*(Y2-Y1))+Y1
            SY = slice(*Y.mapInterval((l,l,"cob")))
            return data[...,SY,SX]
        else:
          return ""

    @exportRpc("setPlotType")
    def setPlotType(self,plotType):
        self._plotType = str(plotType).strip()

    def setPlotTemplate(self, plotTemplate):
        self._plotTemplate = plotTemplate

    def setViewSelection(self, viewSelection):
        self._viewSelection = viewSelection

    def setVariable(self, variable):
        self._variable = variable

    @exportRpc("initRender")
    def initRender(self):
        print 'init render called'
        reply = {"message": "success"}
        self._initRender = True
        return reply

    @exportRpc("stillRender")
    def stillRender(self, options):
        self.f=cdms2.open(self._netcdfFile)
        data = self.f(self._variable)
        self._canvas.clear()
        d = self._canvas.plot(data,self._plotTemplate,self._plotType,bg=1)
        png = d._repr_png_()

        """
        self._canvas.plot(data,self._plotTemplate,self._plotType,bg=1)
        test_filepath='/export/leung25/testIsofill'
        test_png_filepath=test_filepath+'.png'
        test_jpeg_filepath=test_filepath+'.jpeg'
        self._canvas.png(test_png_filepath)
        os.system('convert %s %s'%(test_png_filepath,test_jpeg_filepath))
        img_handler=open(test_jpeg_filepath, 'rb')
        png=base64.b64encode(img_handler.read())
        """
        png = base64.b64encode(png)
        #with open(self._netcdfFile, "rb") as image_file:
        #    imageString = base64.b64encode(image_file.read())
        reply = {}
        if not self._initRender:
            return reply
        import datetime
        reply['image'] = png
        reply['state'] = True
        reply['mtime'] = datetime.datetime.now().time().microsecond
        reply['size'] = [864, 646]
        reply['format'] = "png;base64"
        reply['global_id'] = ""
        reply['localTime'] = ""
        reply['workTime'] = ""
        return reply


class AppProtocol(pv_wamp.PVServerProtocol):
    dataDir = None
    authKey = "vtkweb-secret"
    dsHost = None
    dsPort = 11111
    rsHost = None
    rsPort = 11111
    fileToLoad = None

    def initialize(self):
        # Bring used components
        self.registerVtkWebProtocol(pv_protocols.ParaViewWebStartupRemoteConnection(AppProtocol.dsHost, AppProtocol.dsPort, AppProtocol.rsHost, AppProtocol.rsPort))
        self.registerVtkWebProtocol(pv_protocols.ParaViewWebMouseHandler())
        self.registerVtkWebProtocol(pv_protocols.ParaViewWebViewPort())
        # self.registerVtkWebProtocol(pv_protocols.ParaViewWebViewPortImageDelivery())
        self.registerVtkWebProtocol(pv_protocols.ParaViewWebViewPortGeometryDelivery())
        self.registerVtkWebProtocol(pv_protocols.ParaViewWebTimeHandler())
        self.registerVtkWebProtocol(pv_protocols.ParaViewWebRemoteConnection())

        self._imageDelivery = UWebProtocol()
        self._imageDelivery.setFileName(AppProtocol.fileToLoad)
        self._imageDelivery.setVariable('clt')
        #print self.getDataValueFromCursor(0.5, 0.5)
        self._imageDelivery.setPlotType('boxfill')
        self.registerVtkWebProtocol(self._imageDelivery)

        # Update authentication key to use
        self.updateSecret(AppProtocol.authKey)

# =============================================================================
# Main: Parse args and start server
# =============================================================================
def addArguments(parser):
      """
      Add arguments processed know to this module. parser must be
      argparse.ArgumentParser instance.
      """
      parser.add_argument("-d", "--debug",
            help="log debugging messages to stdout",
            action="store_true")
      parser.add_argument("-p", "--port", type=int, default=8080,
            help="port number on which the server will listen (default: 8080)")
      parser.add_argument("-t", "--timeout", type=int, default=300,
            help="timeout for reaping process on idle in seconds (default: 300s)")
      parser.add_argument("-c", "--content", default=None,
            help="root path of common web content to serve")
      parser.add_argument("-a", "--app-content", default=None, dest='app_content',
            help="root path of application-specific web content to serve")
      parser.add_argument("-k", "--authKey", default=AppProtocol.authKey,
            help="authentication key for clients to connect to the web socket")

      return parser

def startServer(options, protocol=pv_protocols.ParaViewWebProtocol, disableLogging=False):
    """
    Starts the web server. Options must be an object with the following members:
    options.port : port number on which the server will listen
    options.timeout : timeout (seconds) for reaping process on idle
    options.content : root path of common content to serve
    options.app_content : root path of application-specific content to serve
    """
    from twisted.python import log
    from twisted.internet import reactor
    from twisted.web.server import Site
    from twisted.web.static import File

    from autobahn.resource import WebSocketResource

    # TODO Fix this
    #from paraview.webgl import WebGLResource

    if options.content is None and options.app_content is None:
        raise EnvironmentError(0, 'No content specified')

    if not disableLogging:
        log.startLogging(sys.stdout)

    # Set up the server factory
    wampFactory = wamp.ReapingWampServerFactory(
        "ws://localhost:%d" % options.port, options.debug, options.timeout)
    wampFactory.protocol = AppProtocol

    # Set up the site
    root = None
    if options.app_content is None:
        root = File(options.content)
    elif options.content is None:
        root = File(options.app_content)
    else:
        root = File(options.content)
        root.putChild("app", File(options.app_content))

    root.putChild("ws", WebSocketResource(wampFactory))

    # TODO Fix this
    #root.putChild("WebGL", WebGLResource());

    # Start factory and reactor
    wampFactory.startFactory()
    reactor.listenTCP(options.port, Site(root))
    reactor.run()
    wampFactory.stopFactory()

if __name__ == "__main__":
    # Create argument parser
    parser = argparse.ArgumentParser(description="ParaView/Web Pipeline Manager web-application")

    # Add default arguments
    addArguments(parser)

    # Add local arguments
    parser.add_argument("--file", default=None, help="File to load", dest="file")
    parser.add_argument("--ds-host", default=None, help="Hostname to connect to for DataServer", dest="dsHost")
    parser.add_argument("--ds-port", default=11111, type=int, help="Port number to connect to for DataServer", dest="dsPort")
    parser.add_argument("--rs-host", default=None, help="Hostname to connect to for RenderServer", dest="rsHost")
    parser.add_argument("--rs-port", default=11111, type=int, help="Port number to connect to for RenderServer", dest="rsPort")

    # Exctract arguments
    args = parser.parse_args()

    # Configure our current application
    AppProtocol.authKey    = args.authKey
    AppProtocol.dsHost     = args.dsHost
    AppProtocol.dsPort     = args.dsPort
    AppProtocol.rsHost     = args.rsHost
    AppProtocol.rsPort     = args.rsPort
    if args.file is None:
        print 'At least one valid file is required'
    else:
        AppProtocol.fileToLoad = args.file
    
    startServer(options=args)
