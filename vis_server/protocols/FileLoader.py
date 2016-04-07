import os

from . import BaseProtocol
from external import exportRpc

import cdms2
import numpy


class FileLoader(BaseProtocol):

    _file_cache = {}

    def __init__(self, datadir='.'):
        BaseProtocol.__init__(self)
        self._datadir = datadir

    @exportRpc('cdat.file.list_variables')
    def list_variables(self, file_name):
        """Return a list of variables from the given file name."""
        reader = self.get_reader(file_name)
        outVars = {}
        for vname in reader.variables:
            var = reader.variables[vname]

            # Get a displayable name for the variable
            if hasattr(var, 'long_name'):
                name = var.long_name
            elif hasattr(var, 'title'):
                name = var.title
            elif hasattr(var, 'id'):
                name = var.id
            else:
                name = vname
            if hasattr(var, 'units'):
                units = var.units
            else:
                units = 'Unknown'
            axisList = []
            for axis in var.getAxisList():
                axisList.append(axis.id)
            lonLat = None
            if (var.getLongitude() and
                    not isinstance(var.getGrid(), cdms2.grid.AbstractRectGrid)):
                lonName = var.getLongitude().id
                latName = var.getLatitude().id
                lonLat = [lonName, latName]
                # add min/max for longitude/latitude
                if (lonName not in outVars):
                    outVars[lonName] = {}
                lonData = var.getLongitude()[:].data
                outVars[lonName]['bounds'] = [numpy.amin(lonData), numpy.amax(lonData)]
                if (latName not in outVars):
                    outVars[latName] = {}
                latData = var.getLatitude()[:].data
                outVars[latName]['bounds'] = [numpy.amin(latData), numpy.amax(latData)]
            if (isinstance(var.getGrid(), cdms2.grid.AbstractRectGrid)):
                gridType = 'rectilinear'
            elif (isinstance(var.getGrid(), cdms2.hgrid.AbstractCurveGrid)):
                gridType = 'curvilinear'
            elif (isinstance(var.getGrid(), cdms2.gengrid.AbstractGenericGrid)):
                gridType = 'generic'
            else:
                gridType = None
            if (vname not in outVars):
                outVars[vname] = {}
            outVars[vname]['name'] = name
            outVars[vname]['shape'] = var.shape
            outVars[vname]['units'] = units
            outVars[vname]['axisList'] = axisList
            outVars[vname]['lonLat'] = lonLat
            outVars[vname]['gridType'] = gridType
            if ('bounds' not in outVars[vname]):
                outVars[vname]['bounds'] = None
        outAxes = {}
        for aname in reader.axes:
            axis = reader.axes[aname]

            # Get a displayable name for the variable
            if hasattr(axis, 'id'):
                name = axis.id
            else:
                name = aname
            if hasattr(axis, 'units'):
                units = axis.units
            else:
                units = 'Unknown'
            outAxes[aname] = {
                'name': name,
                'shape': axis.shape,
                'units': units,
                'data': axis.getData().tolist()
            }
        return [outVars, outAxes]

    @exportRpc('cdat.file.can_open')
    def can_open(self, file_name):
        """Try to open the given file."""
        full_path = file_name  # append data dir prefix
        if not file_name.startswith('http'):
            full_path = os.path.join(self._datadir, file_name)

        if file_name not in self._file_cache:
            self._file_cache[file_name] = cdms2.open(full_path)

        return file_name in self._file_cache

    def get_reader(self, file_name):
        if self.can_open(file_name):
            return self._file_cache[file_name]
        else:
            raise Exception('cannot open file at ' + file_name)
