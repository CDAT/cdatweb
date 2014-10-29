import sys

try:
    import argparse
except ImportError:
    # since  Python 2.6 and earlier don't have argparse, we simply provide
    # the source for the same as _argparse and we use it instead.
    import _argparse as argparse

from uvis import AppProtocol, startServer

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
      parser.add_argument("-i", "--host", type=str, default='localhost',
            help="the interface for the web-server to listen on (default: localhost)")
      parser.add_argument("-t", "--timeout", type=int, default=300,
            help="timeout for reaping process on idle in seconds (default: 300s)")
      parser.add_argument("-c", "--content", default=None,
            help="root path of common web content to serve")
      parser.add_argument("-a", "--app-content", default=None, dest='app_content',
            help="root path of application-specific web content to serve")
      parser.add_argument("-k", "--authKey", default=AppProtocol.authKey,
            help="authentication key for clients to connect to the web socket")

      return parser

if __name__ == "__main__":

    try:
        from PyQt4 import QtGui
        global qapp
        qapp = QtGui.QApplication(sys.argv)
        import qt4reactor
        import sys
        del sys.modules['twisted.internet.reactor']
        import qt4reactor
        qt4reactor.install()

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

        startServer(options=args)
    except:
        import traceback
        traceback.print_exc()
