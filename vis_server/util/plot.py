'''
This module contains utilities and class that assist in creating new
visualization applications on top of vtkWeb.
'''

import random
import string

_idpool = string.letters + string.digits


class Plot(object):
    '''
    Base class for all plots. This class defines the interface that all
    other plotting class should implement.
    '''

    def __init__(self, *args, **kw):
        '''
        Initialize the plot and assign a unique id. By default, all
        keyword arguments are added to the configuration object and the
        data is initialized to None.
        '''

        #: Stores the instance specific configuration for the plot as a dict.
        self.config = kw

        #: Stores the data used to generate the plot.
        self.data = None

        #: Read only id string.
        self._id = ''.join(
            [random.choice(_idpool) for i in xrange(12)]
        )

        #: Private boolean indicating if create has been called or not
        self._created = False

    @property
    def id(self):
        '''
        Get the unique identifier for this plot.

        :rtype: str
        '''
        return self._id

    def value(self, **kw):
        '''
        Get a value from the data. Subclasses define the format of the
        keyword arguments and the return format.

        :rtype: dict
        '''
        return None

    def create(self):
        '''
        Initialize the plot object after the configuration and data has
        been set.  Calling this function is optional.  It will be called
        automatically by render on first draw.
        '''
        if self._created:
            self.delete()
        self._created = True

    def delete(self):
        '''
        Deletes the current plot object forcing it to be recreated on the
        next render.
        '''
        self._created = False

    def render(self, options):
        '''
        Render the plot into the clients viewport.  Calls
        :py:func:`Plot.create` on the first render.

        :param dict options: Rendering options given to the subclass
        :returns: Success or failure
        :rtype: bool
        '''
        if not self._created:
            self.create()

        return False
