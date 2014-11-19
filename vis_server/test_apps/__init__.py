#!/usr/bin/env python

import cube


def get_apps(cls):
    apps = {}
    apps.update(cube.get_apps(cls))
    return apps

__all__ = ['get_apps']
