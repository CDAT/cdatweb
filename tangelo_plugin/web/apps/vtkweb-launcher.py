#!python

r"""
    This module is a VTK Web server application.
    The following command line illustrate how to use it::

        $ vtkpython .../vtk_web_tree.py

    Any VTK Web executable script come with a set of standard arguments that
    can be overriden if need be::

        --port 8080
             Port number on which the HTTP server will listen to.

        --content /path-to-web-content/
             Directory that you want to server as static web content.  By
             default, this variable is empty which mean that we rely on another
             server to deliver the static content and the current process only
             focus on the WebSocket connectivity of clients.

        --authKey vtk-secret
             Secret key that should be provided by the client to allow it to
             make any WebSocket communication. The client will assume if none
             is given that the server expect "vtk-secret" as secret key.
"""

import imp

# import to process args
import sys
import os

# import vtk modules.
from vtk.web import server, wamp, protocols

# import annotations
from autobahn.wamp import exportRpc

try:
    import argparse
except ImportError:
    # since  Python 2.6 and earlier don't have argparse, we simply provide
    # the source for the same as _argparse and we use it instead.
    import _argparse as argparse

# =============================================================================
# Create custom File Opener class to handle clients requests
# =============================================================================


class VTKWebApp(wamp.ServerProtocol):
    # Application configuration
    view = None
    authKey = "vtkweb-secret"

    def __init__(self, *args, **kw):
        wamp.ServerProtocol.__init__(self)

    @classmethod
    def add_cmd_args(cls, parser):
        '''
        Subclasses can add arguments to the argparser instance.
        '''
        pass

    def initialize(self):
        # Bring used components
        self.registerVtkWebProtocol(protocols.vtkWebMouseHandler())
        self.registerVtkWebProtocol(protocols.vtkWebViewPort())
        self.registerVtkWebProtocol(
            protocols.vtkWebViewPortImageDelivery())
        self.registerVtkWebProtocol(
            protocols.vtkWebViewPortGeometryDelivery())

        # Update authentication key to use
        self.updateSecret(self.authKey)


# =============================================================================
# Main: Parse args and start server
# =============================================================================

if __name__ == "__main__":
    # Get the full path to the user's application file.
    if len(sys.argv) < 2:
        print >>sys.stderr, ("usage: vtkweb-launcher.py " +
                             "[tangelo-vtkweb-app] [arg1, arg2, arg3, ...]")
        sys.exit(1)
    userfile = sys.argv[1]

    sys.path.append(os.path.abspath(os.path.dirname(sys.argv[1])))
    # Import the user file as a module.
    try:
        usermod = imp.load_source("usermod", userfile)
    except IOError:
        print >>sys.stderr, "error: could not open file '%s'" % (userfile)
        sys.exit(2)
    except ImportError as e:
        print >>sys.stderr, "error: could not import module '%s'" % (userfile)
        print >>sys.stderr, "({})".format(e)
        sys.exit(2)
    except Exception as e:
        print >>sys.stderr, "error: unknown exception on import '%s'" % (userfile)
        print >>sys.stderr, "({})".format(e)
        sys.exit(2)

    # Create argument parser
    parser = argparse.ArgumentParser(description="Tangelo/VTKWeb application")

    AppClass = VTKWebApp
    if 'ApplicationFactory' not in usermod.__dict__:
        print >>sys.stderr, "error: invalid application module '%s'" % (userfile)

    AppClass = usermod.ApplicationFactory(AppClass)

    # Add default arguments
    server.add_arguments(parser)

    # Add local arguments, if any are specified in the user module.
    if "add_arguments" in usermod.__dict__:
        AppClass.add_arguments(parser)

    # Extract arguments (dropping the "usermodule" argument first).
    del sys.argv[1]
    opts = parser.parse_args()

    # Configure our current application
    if opts.__dict__.get('authKey'):
        AppClass.authKey = opts.authKey
    VTKWebApp = AppClass(opts)

    # Start server
    server.start_webserver(options=opts, protocol=VTKWebApp)
