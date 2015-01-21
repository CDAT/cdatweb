import traceback
import os

from . import BaseProtocol
from external import exportRpc

from readers import __all__ as readers


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
        print 'fileInfo'
        try:
            reader = self.get_reader(file_name)
        except Exception as e:
            traceback.print_exc()
            raise e
        if reader is None:
            print 'No reader for ' + file_name
            return None

        return reader.getInfo()
