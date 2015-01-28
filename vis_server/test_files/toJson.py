#!/usr/bin/env python

from netCDF4 import Dataset

import sys
import json

pathdesc = {
    'files': {},
    'dirs': {
        'work': {
            'dirs': {
                'tmp': {
                    'files': {}
                },
                'copy': {
                    'files': {}
                },
                'December2014': {
                    'dirs': {
                        '1': {
                            'files': {}
                        }
                    },
                    'files': {}
                }
            }
        },
        'climate': {
            'files': {}
        }
    }
}
obj = {
    'files': {}
}
for fname in sys.argv[1:]:
    f = Dataset(fname, 'r')
    fobj = {
        'dimensions': {},
        'attributes': {},
        'variables': {}
    }
    obj['files'][fname] = fobj

    for name in f.dimensions:
        fobj['dimensions'][name] = {
            'units': None,
            'dtype': 'f',
            'type': 'unknown',
            'size': len(f.dimensions[name])
        }
    for name in f.ncattrs():
        fobj['attributes'][name] = getattr(f, name)

    for name in f.variables:
        v = f.variables[name]

        fobj['variables'][name] = {
            'attributes': {},
            'axes': v.dimensions,
            'shape': v.shape
        }
        for attr in v.ncattrs():
            fobj['variables'][name]['attributes'][attr] = getattr(v, attr)


tree = {}
def buildTree(root, path):
    root['files'] = {}
    root['dirs'] = {}
    if 'files' in path:
        root['files'] = dict(obj['files'])
    for d in path.get('dirs', {}):
        root['dirs'][d] = {}
        buildTree(root['dirs'][d], path['dirs'][d])

buildTree(tree, pathdesc)
print json.dumps(tree, default=str)
