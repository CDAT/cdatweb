import os

from . import BaseProtocol
from external import exportRpc

from readers.cdms_reader import CdmsReader as Reader


class FileLoader(BaseProtocol):

    _file_cache = {}

    def __init__(self, datadir='.'):
        BaseProtocol.__init__(self)
        self._datadir = datadir

    def get_reader(self, file_name):
        if self._file_cache.get(file_name, 0) is 0:
            self._file_cache[file_name] = None
            if file_name.startswith('http'):
                full_path = file_name
            else:
                full_path = os.path.join(
                    self._datadir,
                    file_name
                )
            if Reader.canOpen(full_path):
                self._file_cache[file_name] = Reader(full_path)
            else:
                raise Exception('cannot open file at ' + file_name)

        return self._file_cache.get(file_name)

    @exportRpc('file.server.info')
    def fileInfo(self, file_name):
        reader = self.get_reader(file_name)
        if reader is None:
            return None

        return reader.getInfo()

    @classmethod
    def get_cached_reader(cls, file_name):
        return cls._file_cache.get(file_name)
