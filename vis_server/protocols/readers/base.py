
class BaseFileReader(object):
    '''
    Super class for file readers providing a unified interface for the rpc
    calls.
    '''

    name = ''
    def __init__(self, file_name):
        '''
        Open a local file for reading.
        '''
        if not self.canOpen(file_name):
            raise Exception('Unhandled file type')
        self._file_name = file_name
        self._file = self._open(file_name)

    def _open(self, file_name):
        '''
        Abstract function to open a file for reading.
        '''
        raise Exception('Unimplemented base class method')

    @classmethod
    def canOpen(self, file_name):
        '''
        Returns True if the file can be handled.
        '''
        return False

    def getInfo(self):
        '''
        Returns an object containing information about the current file.
        '''
        return {
            'variables': {},
            'dimensions': {},
            'attributes': {},
        }

    def getVarInfo(self, var_name):
        '''
        Returns information about a variable.
        '''
        return {
            'attributes': {},
            'axes': [],
            'shape': [],
            'time': None,
            'level': None,
            'latitude': None,
            'longitude': None
        }

    def read(self, var_name):
        '''
        Return an object that can be passed to a visualizer for display.
        '''
        return None

    def export(self):
        pass
