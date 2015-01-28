import json
from os.path import join

import settings

settings.SERVER_TEST = True
from protocols.readers.base import BaseFileReader

class TestReader(BaseFileReader):

    name = 'test'

    @classmethod
    def canOpen(self, file_name):
        try:
            json.loads(open(file_name).read())
            return True
        except Exception:
            return False

    def _open(self, file_name):
        self._content = json.loads(open(file_name).read())
        self._content['dimensions'] = {}
        self._content['attributes'] = {}

    def getInfo(self):
        return self._content


def write_dir(tree, path):
    for f in tree.get('files', {}):
        open(join(path, f), 'w').write(json.dumps(tree['files'][f]))
    for d in tree.get('dirs', {}):
        write_dir(tree['dirs'][d], join(path, d))

if __name__ == '__main__':
    import json
    import sys

    assert len(sys.argv) == 3
    root = sys.argv[1]
    tree = json.loads(open(sys.argv[2]).read())
