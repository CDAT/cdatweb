
'''
This module exposes methods that query for available files.  For the
moment it only supports local files, but eventually it will be expanded
to support remote files as well.
'''
import traceback
import os

from . import BaseProtocol
from external import exportRpc

from FileLoader import FileLoader


class FileFinder(BaseProtocol):

    #: cache of the file system
    _file_tree = None

    def __init__(self, datadir):
        BaseProtocol.__init__(self)
        datadir = datadir.rstrip('/')
        self._datadir = datadir
        self._loader = FileLoader(datadir)

    @exportRpc('file.server.list')
    def list(self):
        if self._file_tree is None:
            self._generate()

        return self._file_tree

    def _generate(self):
        r = {'nodes': [], 'text': '/', 'full': self._datadir}
        self._file_tree = r['nodes']

        roots = {'.': r}
        for root, dirs, files in os.walk(self._datadir, followlinks=True):

            root = root.replace(self._datadir, '', 1)
            root = '.' + root
                

            obj = roots.get(root)
            if obj is None:
                print 'Warning: Problem generating dir tree from "' + root + '"'
                continue

            for d in dirs:
                full = os.path.join(root, d)
                newobj = {
                    'text': d,
                    'nodes': [],
                    'full': full,
                    'type': 'directory'
                }
                obj['nodes'].append(newobj)
                roots[full] = newobj

            for f in files:
                full = os.path.join(root, f)
                if self._loader.get_reader(full):
                    obj['nodes'].append({
                        'text': f,
                        'full': full,
                        'type': 'file'
                    })

        # remove empty subtrees
        def has_files(root):
            result = False
            for i, node in enumerate(root['nodes']):
                if node['type'] == 'file':
                    result = True
                else:
                    local = has_files(node)
                    if not local:
                        root['nodes'].pop(i)
                    result = result or local
            return result

        has_files(r)
