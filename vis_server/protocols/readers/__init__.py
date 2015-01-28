from settings import SERVER_TEST

if not SERVER_TEST:
    from cdms_reader import Cdms_reader
    __all__ = [Cdms_reader]
else:
    from testing import TestReader
    __all__ = [TestReader]

_reader_map = { reader.name: reader for reader in __all__ }


def get_reader(name):
    '''
    Get a reader from its unique name.  If no reader is found,
    returns None.
    '''
    return _reader_map.get(name, None)
