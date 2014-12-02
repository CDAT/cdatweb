import cherrypy
import os
import tangelo
import tangelo.util
import autobahn.websocket as ab_websocket
import autobahn.wamp as wamp
import twisted.internet.reactor
import subprocess
import threading
import ws4py
import sys
import time

#: application name -> application file
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from apps.util import applications as _application


def initialize():
    global vtkpython
    global weblauncher
    global processes

    # Get the module config.
    config = tangelo.plugin_config()

    # Raise an error if there's no vtkpython executable.
    vtkpython = config.get("vtkpython", None)
    if not vtkpython:
        msg = "No 'vtkpython' option specified in configuration plugin"
        tangelo.log("VTKWEB", "[initialization] fatal error: %s" % (msg))

        # Construct a run() function that will mask the restful API and just
        # inform the caller about the configuration problem.
        def run():
            tangelo.http_status(400, "Bad Configuration")
            return {"error": msg}

        sys.modules[__name__].__dict__["run"] = run
        return

    vtkpython = tangelo.util.expandpath(vtkpython)
    tangelo.log("VTKWEB", "[initialization] Using vtkpython executable %s" % (vtkpython))

    # Use the "web launcher" included with the plugin.
    weblauncher = os.path.realpath("%s/apps/vtkweb-launcher.py" % (os.path.dirname(__file__)))

    # Initialize a table of VTKWeb processes.
    tangelo.plugin_store()["processes"] = processes = {}

    # Check to see if a reactor is running already.
    if twisted.internet.reactor.running:
        threads = [t for t in threading.enumerate() if t.name == "tangelo-vtkweb-plugin"]
        if len(threads) > 0:
            tangelo.log(
                "VTKWEB",
                "[initialization] A reactor started by a previous loading of "
                "this plugin is already running"
            )
        else:
            tangelo.log(
                "VTKWEB",
                "[initialization] A reactor started by someone other than "
                "this plugin is already running"
            )
    else:
        # Start the Twisted reactor, but in a separate thread so it doesn't
        # block the CherryPy main loop.  Mark the thread as "daemon" so that
        # when Tangelo's main thread exits, the reactor thread will be killed
        # immediately.
        reactor = threading.Thread(
            target=twisted.internet.reactor.run,
            kwargs={
                "installSignalHandlers": False
            },
            name="tangelo-vtkweb-plugin"
        )
        reactor.daemon = True
        reactor.start()

        tangelo.log("VTKWEB", "[initialization] Starting Twisted reactor")

initialize()


def query_key(key):
    # Error for bad key.
    if key not in processes:
        tangelo.http_status(400, "No Such Process Key")
        return {"error": "Requested key not in process table"}

    # Retrieve the process entry.
    rec = processes[key]
    response = {"status": "complete",
                "process": "running",
                "port": rec["port"],
                "stdout": rec["stdout"].readlines(),
                "stderr": rec["stderr"].readlines()}

    # Check the status of the process.
    returncode = rec["process"].poll()
    if returncode is not None:
        # Since the process has ended, delete the process object.
        del processes[key]

        # Fill out the report response.
        response["process"] = "terminated"
        response["returncode"] = returncode

    return response


@tangelo.restful
def post(*pargs, **query):
    args = query.get("args", "")
    timeout = float(query.get("timeout", 0))

    if not (pargs[-1] in _application):
        tangelo.http_status(400, "Invalid request")
        return None

    # Check the user arguments.
    userargs = args.split()
    if "--port" in userargs:
        tangelo.http_status(400, "Illegal Argument")
        return {"error": "You may not specify '--port' among the arguments passed in 'args'"}

    program = os.path.join(
        os.path.dirname(weblauncher),
        _application[pargs[-1]]['path']
    )

    # Obtain an available port.
    port = tangelo.util.get_free_port()

    # Generate a unique key.
    key = tangelo.util.generate_key(processes.keys())

    # Detect http vs. https
    scheme = "ws"
    ssl_key = cherrypy.config.get("server.ssl_private_key")
    ssl_cert = cherrypy.config.get("server.ssl_certificate")

    # Generate command line.
    cmdline = [vtkpython, weblauncher, program, "--port", str(port)] + userargs
    if ssl_key and ssl_cert:
        scheme = "wss"
        cmdline.extend(["--sslKey", ssl_key, "--sslCert", ssl_cert])

    # Launch the requested process.
    tangelo.log("VTKWEB", "Starting process: %s" % (" ".join(cmdline)))
    try:
        process = subprocess.Popen(cmdline,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
    except (OSError, IOError) as e:
        tangelo.log("VTKWEB", "Error:  could not launch VTKWeb process")
        return {"error": e.strerror}

    # Capture the new process's stdout and stderr streams in
    # non-blocking readers.
    stdout = tangelo.util.NonBlockingReader(process.stdout)
    stderr = tangelo.util.NonBlockingReader(process.stderr)

    # Read from stdout to look for the signal that the process has
    # started properly.
    class FactoryStarted:
        pass

    class Failed:
        pass

    class Timeout:
        pass
    signal = "Starting factory"
    if timeout <= 0:
        timeout = 10
    sleeptime = 0.5
    wait = 0
    saved_lines = []
    try:
        while True:
            lines = stdout.readlines()
            saved_lines += lines
            for line in lines:
                if line == "":
                    # This indicates that stdout has closed without
                    # starting the process.
                    raise Failed()
                elif signal in line:
                    # This means that the server has started.
                    raise FactoryStarted()

            # If neither failure nor success occurred in the last block
            # of lines from stdout, either time out, or try again after
            # a short delay.
            if wait >= timeout:
                raise Timeout()

            wait += sleeptime
            time.sleep(sleeptime)
    except Timeout:
        tangelo.http_status(524, "Timeout")
        return {"error": "Process startup timed out"}
    except Failed:
        tangelo.http_status(500)
        return {"error": "Process did not start up properly",
                "stdout": saved_lines,
                "stderr": stderr.readlines()}
    except FactoryStarted:
        stdout.pushlines(saved_lines)

    # Create a websocket handler path dedicated to this process.
    host = "localhost" if cherrypy.server.socket_host == "0.0.0.0" else cherrypy.server.socket_host
    tangelo.websocket.mount(key, WebSocketRelay(host, port, key), "wamp")

    # Log the new process in the process table, including non-blocking
    # stdout and stderr readers.
    processes[key] = {"port": port,
                      "process": process,
                      "stdout": stdout,
                      "stderr": stderr}

    # Form the websocket URL from the hostname/port used in the
    # request, and the newly generated key.
    url = "%s://%s/ws/%s/ws" % (scheme, cherrypy.request.base.split("//")[1], key)
    return {"key": key,
            "url": url}


@tangelo.restful
def delete(key=None):
    # TODO(choudhury): shut down a vtkweb process by key after a given timeout.

    if key is None:
        tangelo.http_status(400, "Required Argument Missing")
        return {"error": "'key' argument is required"}

    # Check for the key in the process table.
    if key not in processes:
        tangelo.http_status(400, "Key Not Found")
        return {"error": "Key %s not in process table" % (key)}

    # Terminate the process.
    tangelo.log("VTKWEB", "Shutting down process %s" % (key))
    proc = processes[key]
    proc["process"].terminate()
    proc["process"].wait()
    tangelo.log("VTKWEB", "Process terminated")

    # Remove the process entry from the table.
    del processes[key]

    return {"key": key}


def VTKWebSocketAB(url, relay):
    class RegisteringWebSocketClientFactory(wamp.WampClientFactory):
        def register(self, client):
            self.client = client

    class Protocol(wamp.WampClientProtocol):
        def onOpen(self):
            self.factory.register(self)

        def onMessage(self, msg, is_binary):
            relay.send(msg)

    class Connection(threading.Thread):
        def run(self):
            self.factory = RegisteringWebSocketClientFactory(url)
            self.factory.protocol = Protocol
            twisted.internet.reactor.callFromThread(ab_websocket.connectWS,
                                                    self.factory)

        def send(self, data):
            twisted.internet.reactor.callFromThread(Protocol.sendMessage,
                                                    self.factory.client,
                                                    data)

    c = Connection()
    c.start()
    return c


def WebSocketRelay(hostname, port, key):
    class Class(ws4py.websocket.WebSocket):
        def __init__(self, *pargs, **kwargs):
            ws4py.websocket.WebSocket.__init__(self, *pargs, **kwargs)

            scheme = "ws"
            if cherrypy.config.get("server.ssl_private_key"):
                scheme = "wss"
            url = "%s://%s:%d/ws" % (scheme, hostname, port)

            tangelo.log("VTKWEB", "websocket created at %s:%d/%s (proxy to %s)" %
                        (hostname, port, key, url))

            self.client = VTKWebSocketAB(url, self)

        def closed(self, code, reason=None):
            # TODO(choudhury): figure out if recovery, etc. is possible if the
            # socket is closed for some reason.
            tangelo.log("VTKWEB", "websocket at %s:%d/%s closed with code %d (%s)" %
                        (hostname, port, key, code, reason))

        def received_message(self, msg):
            self.client.send(msg.data)

    return Class
