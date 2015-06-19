"""Py Test configuration that mocks out VTK when it is not importable."""

import sys
import os

root = os.path.abspath(
    os.path.dirname(__file__)
)
sys.path.append(root)
sys.path.append(
    os.path.join(
        root,
        'test'
    )
)

try:
    import vtk  # noqa
except ImportError:
    vtk = __import__('mock_vtk')
    sys.modules['vtk'] = vtk
    sys.modules['autobahn'] = __import__('mock_autobahn')

sys.path.append(os.path.dirname(vtk.__file__))  # noqa

try:
    import vcs  # noqa
except ImportError:
    sys.modules['vcs'] = __import__('mock_vcs')

try:
    import cdms2  # noqa
except ImportError:
    sys.modules['cdms2'] = __import__('mock_cdms2')
