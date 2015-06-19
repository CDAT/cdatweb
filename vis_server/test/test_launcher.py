"""Test the vtkweb launcher."""

import time
import sys
import os
import shutil
import tempfile
from subprocess import Popen, STDOUT, PIPE
from unittest import TestCase
import json

import requests

port = int(os.environ.get('TEST_PORT', 21435))
coverage = os.environ.get('COVERAGE_COMMAND', 'coverage')
cov_args = os.environ.get('COVERAGE_ARGS', '-p')
root = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')
)  # path to vis_server
debug = os.environ.get('DEBUG_OUTPUT', 'no')
launcher = 'http://localhost:%i/vtk' % port
run = os.path.join(root, 'test', 'test.sh')
tmp = os.path.join(tempfile.gettempdir(), 'tmp')
if not os.path.exists(tmp):
    os.mkdir(tmp)

sys.path.append(root)

#: Launcher config for testing
config = json.dumps({
    "configuration": {
        "host": "localhost",
        "port": port,
        "endpoint": "vtk",
        "proxy_file": tmp + "/proxy.txt",
        "sessionURL": "ws://${host}:${port}/ws",
        "timeout": 5,
        "log_dir": tmp,
        "fields": []
    },
    "sessionData": {"upDir": tmp},
    "resources": [
        {"host": "localhost", "port_range": [9001, 9005]}
    ],
    "properties": {
        "test_dir": root,
        "log_dir": tmp,
        "data_dir": tmp
    },
    "apps": {
        "basic": {
            "cmd": [
                run, "basic"
            ],
            "ready_line": "Starting"
        },
        "fail": {
            "cmd": [
                run, "fail"
            ],
            "ready_line": "Starting"
        },
        "timeout": {
            "cmd": [
                run, "timeout"
            ],
            "ready_line": "Starting"
        }
    }
})


class LauncherTest(TestCase):

    """Tests for the vtkweb launcher."""

    @classmethod
    def setUpClass(cls):  # noqa
        """Start up the launcher service with the test config."""
        # Write the config to a temporary file
        cls._config = tempfile.NamedTemporaryFile()
        cls._config.write(config)
        cls._config.seek(0)

        # Start the vis launcher service
        cls._server = Popen(
            ' '.join([
                coverage,
                'run',
                cov_args,
                'launcher.py',
                cls._config.name
            ]),
            cwd=root,
            shell=True,
            stderr=STDOUT,
            stdout=PIPE
        )
        time.sleep(1)

    @classmethod
    def tearDownClass(cls):  # noqa
        """Clean up the temporary files and stops the server."""
        global debug
        cls._server.poll()
        if cls._server.returncode is not None:
            debug = 'yes'

        cls._server.kill()
        if debug != 'no':
            sys.stderr.write('** SERVER LOG **\n')
            sys.stderr.write(cls._server.stdout.read())
            sys.stderr.write('** END SERVER LOG **\n')
        del cls._config
        shutil.rmtree(tmp)

    def test_basic(self):
        """Chack basic operation of the launcher."""
        data = json.dumps({'application': 'basic'})
        req = requests.post(
            launcher,
            data=data
        )
        self.assertTrue(req.ok)
        resp = req.json()
        self.assertIn('id', resp)
        self.assertIn('sessionURL', resp)
        self.assertNotIn('error', resp)

        req = requests.get(
            launcher + '/' + resp['id']
        )
        self.assertTrue(req.ok)
        stat = req.json()
        self.assertNotIn('error', stat)
        self.assertEqual(stat['id'], resp['id'])

        req = requests.delete(
            launcher + '/' + resp['id']
        )
        self.assertNotEqual(req.status_code, 404)

        req = requests.get(
            launcher + '/' + resp['id']
        )
        self.assertFalse(req.ok)

    def test_bad_application(self):
        """Test a failed application."""
        req = requests.post(
            launcher,
            data='{"application": "unknown"}'
        )
        self.assertFalse(req.ok)

    def test_start_fail(self):
        """Test launcher start failure."""
        req = requests.post(
            launcher,
            data='{"application": "fail"}'
        )
        self.assertIn('error', req.json())

    def test_start_timeout(self):
        """Test launcher timeout."""
        req = requests.post(
            launcher,
            data='{"application": "timeout"}'
        )
        self.assertIn('error', req.json())

if __name__ == '__main__':
    import unittest
    unittest.main()
