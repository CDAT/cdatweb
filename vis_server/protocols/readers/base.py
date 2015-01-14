
class BaseFileReader(object):
    '''
    Super class for file readers providing a unified interface for the rpc
    calls.
    '''

    @classmethod
    def canOpen(self, file_name):
        '''
        Returns True if the file can be handled.
        '''
        return False

    @classmethod
    def getInfo(self, file_name):
        '''
        Returns an object containing information about the given file.
        '''
        return {
            'variables': {},
            'dimensions': {},
            'attributes': {},
        }

    @classmethod
    def getVarInfo(self, file_name, var_name):
        '''
        Returns information about a variable.
        '''
        return {
            'attributes': {},
            'axes': [],
            'time': None,
            'level': None,
            'latitude': None,
            'longitude': None
        }

    @classmethod
    def getVariable(self, file_name, var_name):
        '''
        Return an object that can be passed to a visualizer for display.
        '''
        return None
