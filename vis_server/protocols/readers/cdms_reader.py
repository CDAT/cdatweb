import traceback
import cdms2
from .base import BaseFileReader


def _dim_type(d):
    if d.isLatitude():
        return 'latitude'
    elif d.isLongitude():
        return 'longitude'
    elif d.isTime():
        return 'time'
    elif d.isLevel():
        return 'level'
    else:
        return 'unknown'


class Cdms_reader(BaseFileReader):
    '''
    A reader based on the cdms2 python library.
    '''

    def _open(self, file_name):
        self._f = cdms2.open(file_name)
        self._info = None

    @classmethod
    def canOpen(self, file_name):
        try:
            cdms2.open(file_name)
        except Exception as e:
            traceback.print_exc()
            return False
        return True

    def _getInfo(self):
        variables = {}
        for var, info in self._f.variables.iteritems():
            variables[var] = {
                'dims': info.getAxisIds(),
                'shape': info.getShape(),
                'attributes': dict(info.attributes),
                'description': getattr(info, 'title', ''),
                'dtype': info.typecode(),
                'units': info.units
            }
        dimensions = {}
        for dim, info in self._f.axes.iteritems():
            dimensions[dim] = {
                'units': info.units,
                'dtype': info.typecode(),
                'type': _dim_type(info),
                'data': info.getData().tolist(),
                'size': len(info)
            }
        attributes = dict(self._f.attributes)
        return {
            'variables': variables,
            'dimensions': dimensions,
            'attributes': attributes
        }

    def getInfo(self):
        if self._info is None:
            self._info = self._getInfo()
        return self._info

    def read(self):
        # probably have to define a real api here:
        return self._f
