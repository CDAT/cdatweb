"""Module defining the interface for server side file browsing.

This module exposes methods that query for available files.  For the
moment it only supports local files, but eventually it will be expanded
to support remote files as well.
"""

import os

from . import BaseProtocol
from external import exportRpc

from FileLoader import FileLoader


class FileFinder(BaseProtocol):

    """Server-side file browser protocol.

    This class is resposible for generating (and caching) available files
    on the server.  The response to the exposed `list` method is a tree
    like object compatible with the bootstrap-treeview plugin.
    """

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
                    'type': 'directory',
                    'icon': 'fa fa-folder-open cdat-icon-folder',
                    'selectable': False
                }
                obj['nodes'].append(newobj)
                roots[full] = newobj

            for f in files:
                full = os.path.join(root, f)
                info = self._loader.fileInfo(full)
                tags = []
                icon = 'fa fa-exlamation-triangle cdat-icon-alert'
                readable = False
                if info is not None:
                    icon = 'fa fa-file cdat-icon-normal'
                    tags = [str(len(info['variables']))]
                    readable = True

                else:
                    # this will remove the files from the list entirely
                    # remove to keep them
                    continue

                newobj = {
                    'readable': readable,
                    'text': f,
                    'info': info,
                    'full': full,
                    'type': 'file',
                    'icon': icon,
                    'selectable': False,
                    'collapsed': True,
                    'tags': tags
                }
                if info:
                    vlist = info['variables']
                    if len(vlist):
                        newobj['nodes'] = map(
                            lambda v: {
                                'text': v,
                                'type': 'variable',
                                'info': vlist[v],
                                'file': full,
                                'icon': 'fa fa-arrows-alt fa-lg',
                                'selectable': False
                            },
                            vlist
                        )
                obj['nodes'].append(newobj)

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
