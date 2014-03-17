# Import necessary modules
import os
import sys

import MV2
import json

import types

# Import VTKWeb / ParaViewWeb modules
from vtk.web import wamp
from paraview.web import wamp      as pv_wamp
from paraview.web import protocols as pv_protocols

from vtk.web import server

import protocol
from plot import *

try:
    import argparse
except ImportError:
    # since  Python 2.6 and earlier don't have argparse, we simply provide
    # the source for the same as _argparse and we use it instead.
    import _argparse as argparse

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



        self._imageDelivery = protocol.UVisProtocol()
        self.registerVtkWebProtocol(self._imageDelivery)

        # Update authentication key to use
        self.updateSecret(AppProtocol.authKey)

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
        "ws://%s:%d" % (options.host, options.port), options.debug, options.timeout)
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

