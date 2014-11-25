'''
This module serves to provide a central location for storing all
server wide settings.  (TODO: add file/commandline config options)
'''
import os

#: The path to the local data store
DATA_DIRECTORY = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        '..',
        '..',
        'tmp'
    )
)
