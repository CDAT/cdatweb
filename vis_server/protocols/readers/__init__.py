from cdms_reader import Cdms_reader
__all__ = [Cdms_reader]

_reader_map = {reader.name: reader for reader in __all__}


def get_reader(name):
    '''
    Get a reader from its unique name.  If no reader is found,
    returns None.
    '''
    return _reader_map.get(name, None)
