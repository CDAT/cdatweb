from settings import SERVER_TEST

if not SERVER_TEST:
    from cdms_reader import Cdms_reader
    all_readers = [Cdms_reader]
else:
    from testing import TestReader
    all_readers = [TestReader]

_reader_map = {reader.name: reader for reader in all_readers}


def get_reader(name):
    '''
    Get a reader from its unique name.  If no reader is found,
    returns None.
    '''
    return _reader_map.get(name, None)
