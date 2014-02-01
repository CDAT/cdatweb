# Import necessary modules
import os
import sys

import MV2
import json

import types

from plot import *

# Import VTKWeb / ParaViewWeb modules
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

#//////////////////////////////////////////////////////////////////////////////
#
# Helper function to bind RPC
#
#//////////////////////////////////////////////////////////////////////////////
def bindRpc(cls, ns, name, mctor):
  fullName = name
  rpcName = name

  if ns is not None:
    rpcName = ns + ':' + name
    fullName = '__' + ns + '_' + name

  rpc = types.MethodType(exportRpc(rpcName)(mctor(fullName)), None, cls)
  setattr(cls, fullName, rpc)

#//////////////////////////////////////////////////////////////////////////////
#
# Helper function to add mapped RPC
#
#//////////////////////////////////////////////////////////////////////////////
def addMappedRpc(cls, objs, ns, call):
  call_lc = call[0].lower() + call[1:]

  def createRpc(call):
    def dispatchRpc(self, i, *args, **kwargs):
      c = getattr(self, objs)
      if i in c:
        return getattr(c[i], call_lc)(*args, **kwargs)
    return dispatchRpc

  bindRpc(cls, ns, call, createRpc)

#//////////////////////////////////////////////////////////////////////////////
#
# Web protocol for uvis framework
#
#//////////////////////////////////////////////////////////////////////////////
class UVisProtocol(pv_protocols.ParaViewWebProtocol):
    def __init__(self):
        self._plots = {}
        self._nextPlot = -1

    @exportRpc
    def createPlot(self, plotId, *args, **kwargs):
          pl = PlotFactory.createPlot(plotId, *args, **kwargs);
          self._nextPlot += 1
          i = self._nextPlot
          self._plots[i]= pl
          return i

    @exportRpc("stillRender")
    def stillRender(self, options):
        if options['view'] != -1:
            return self._plots[options['view']].render(options);

#//////////////////////////////////////////////////////////////////////////////
#
# Application protocol
#
#//////////////////////////////////////////////////////////////////////////////
class AppProtocol(pv_wamp.PVServerProtocol):
    dataDir = None
    authKey = "vtkweb-secret"
    dsHost = None
    dsPort = 11111
    rsHost = None
    rsPort = 11111

    def initialize(self):
        # Bring used components
        self.registerVtkWebProtocol(pv_protocols.ParaViewWebStartupRemoteConnection(
          AppProtocol.dsHost, AppProtocol.dsPort, AppProtocol.rsHost, AppProtocol.rsPort))

        self._imageDelivery = UVisProtocol()

        self.registerVtkWebProtocol(pv_protocols.ParaViewWebMouseHandler())
        self.registerVtkWebProtocol(pv_protocols.ParaViewWebViewPort())
        self.registerVtkWebProtocol(pv_protocols.ParaViewWebViewPortGeometryDelivery())
        self.registerVtkWebProtocol(pv_protocols.ParaViewWebTimeHandler())
        self.registerVtkWebProtocol(pv_protocols.ParaViewWebRemoteConnection())
        self.registerVtkWebProtocol(self._imageDelivery)

        # Update authentication key to use
        self.updateSecret(AppProtocol.authKey)

#//////////////////////////////////////////////////////////////////////////////
#
# Main: Parse args and start server
#
#//////////////////////////////////////////////////////////////////////////////
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

#//////////////////////////////////////////////////////////////////////////////
#
# Start PVWeb server
#
#//////////////////////////////////////////////////////////////////////////////
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
    parser.add_argument("--ds-host", default=None, help="Hostname to connect to for DataServer",
                        dest="dsHost")
    parser.add_argument("--ds-port", default=11111, type=int, help="Port number to connect to for DataServer",
                        dest="dsPort")
    parser.add_argument("--rs-host", default=None, help="Hostname to connect to for RenderServer", dest="rsHost")
    parser.add_argument("--rs-port", default=11111, type=int, help="Port number to connect to for RenderServer",
                        dest="rsPort")

    # Exctract arguments
    args = parser.parse_args()

    # Configure our current application
    AppProtocol.authKey    = args.authKey
    AppProtocol.dsHost     = args.dsHost
    AppProtocol.dsPort     = args.dsPort
    AppProtocol.rsHost     = args.rsHost
    AppProtocol.rsPort     = args.rsPort

    for rpc in ("id", "setId", "data", "setData", "createContext", "render", "getValueAt", "error"):
        addMappedRpc(UVisProtocol, "_plots", "plot", rpc)

    startServer(options=args)
