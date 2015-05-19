import os

from . import BaseProtocol
from external import exportRpc

from readers import all_readers as readers


class FileLoader(BaseProtocol):

    _file_cache = {}

    def __init__(self, datadir):
        BaseProtocol.__init__(self)
        self._datadir = datadir

    def get_reader(self, file_name):
        if self._file_cache.get(file_name, 0) is 0:
            self._file_cache[file_name] = None
            full_path = os.path.join(
                self._datadir,
                file_name
            )
            for reader in readers:
                if reader.canOpen(full_path):
                    self._file_cache[file_name] = reader(full_path)
                    break

        return self._file_cache[file_name]

    @exportRpc('file.server.info')
    def fileInfo(self, file_name):
        reader = self.get_reader(file_name)
        if reader is None:
            return None

        return reader.getInfo()

    @classmethod
    def get_cached_reader(cls, file_name):
        return cls._file_cache.get(file_name)
