#!/usr/bin/env python

import cube
import dv3d


def get_apps(cls):
    apps = {}
    apps.update(cube.get_apps(cls))
    apps.update(dv3d.get_apps(cls))
    return apps

__all__ = ['get_apps']
