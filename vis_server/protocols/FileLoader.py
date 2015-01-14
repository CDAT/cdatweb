from ..external import exportRpc
from ..protocols import BaseProtocol

from readers import __all__ as readers


class FileLoader(BaseProtocol):

    @classmethod
    def get_reader(cls, file_name):
        for reader in readers:
            if reader.canOpen(file_name):
                return reader
        return None

    @exportRpc('fileLoader.fileInfo')
    def fileInfo(self, file_name):
        reader = self.get_reader(file_name)
        if reader is None:
            return None

        return reader.getInfo(file_name)

    @exportRpc('fileLoader.varInfo')
    def varInfo(self, file_name, var_name):
        reader = self.get_reader(file_name)
        if reader is None:
            return None

        return reader.getVarInfo(file_name, var_name)
