#!/usr/bin/env python

import urllib2
import sys
import os
import cdms2
import vcs

tmp = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'tmp')
)


def create_context(fname, varname):
    f = cdms2.open(fname)
    parameters = {
        'VerticalScaling': 3.0,
        'ToggleVolumePlot': vcs.off,
        'ScaleOpacity': [1.0, 1.0],
        'ToggleSurfacePlot': vcs.off,
        'ScaleColormap': [-10.0, 10.0, 1],
        'BasemapOpacity': [0.5],
        'XSlider': (-50.0, vcs.on),
        'ZSlider': (10.0, vcs.on),
        'YSlider': (20.0, vcs.on),
    }
    var = f[varname](squeeze=1)

    canvas = vcs.init()
    gm = vcs.get3d_scalar('default')

    for param in parameters:
        gm.setParameter(param[0], param[1])

    canvas.plot(
        var,
        gm,
        cdmsfile=f.id,
        window_size=(900, 600)
    )

    plot = canvas.backend.plotApps[gm]
    return plot.getRenderWindow()


def get_apps(cls):

    class DV3DVolume(cls):

        _view = None
        _file = os.path.join(tmp, 'geos5-test.nc')
        _var = 'uwnd'

        @classmethod
        def _renderActiveView(cls):
            cls._view = create_context(cls._file, cls._var)

    _url = 'https://uv-cdat.github.io/cdatweb/data/geos5-test.nc'
    if not os.path.isfile(DV3DVolume._file):
        print >> sys.stderr, "Downloading test file from " + _url
        open(DV3DVolume._file, 'wb').write(
            urllib2.urlopen(_url).read()
        )
        print >> sys.stderr, "Saved to: " + DV3DVolume._file

    return {
        'dv3d': DV3DVolume
    }
