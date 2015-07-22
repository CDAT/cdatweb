import os

from . import BaseProtocol
from external import exportRpc

import cdms2


class FileLoader(BaseProtocol):

    _file_cache = {}

    def __init__(self, datadir='.'):
        BaseProtocol.__init__(self)
        self._datadir = datadir

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
