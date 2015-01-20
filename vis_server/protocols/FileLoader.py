from . import BaseProtocol
from external import exportRpc

from readers import __all__ as readers


class FileLoader(BaseProtocol):

    _file_cache = {}

    @classmethod
    def get_reader(cls, file_name):
        if cls._file_cache.get(file_name, 0) is 0:
            for reader in readers:
                if reader.canOpen(file_name):
                    cls._file_cache[file_name] = reader(file_name)
                    break

        return cls._file_cache[file_name]

    @exportRpc('file.server.info')
    def fileInfo(self, file_name):
        reader = self.get_reader(file_name)
        if reader is None:
            return None

        return reader.getInfo()
