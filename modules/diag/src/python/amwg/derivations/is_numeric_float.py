#!/usr/bin/python -tt
#=======================================================================
#                        General Documentation

"""Single-function module.

   See function docstring for description.
"""

#-----------------------------------------------------------------------
#                       Additional Documentation
#
# RCS Revision Code:
#   $Id: is_numeric_float.py,v 1.1 2004/02/19 22:28:12 jlin Exp $
#
# Modification History:
# - 08 Oct 2003:  Original by Johnny Lin, Computation Institute,
#   University of Chicago.  Email:  air_jlin@yahoo.com.  Passed
#   passably reasonable tests.
#
# Notes:
# - Written for Python 2.2.2.
# - Module docstrings can be tested using the doctest module.  To
#   test, execute "python is_numeric_float.py".
# - Non-built-in packages and modules required:  Numeric
#
# Copyright (c) 2003 by Johnny Lin.  For licensing, distribution 
# conditions, contact information, and additional documentation see
# the URL http://www.johnny-lin.com/py_pkgs/atmqty/.
#=======================================================================




#---------------- Module General Import and Declarations ---------------

#- Set module version number to package version number:

import package_version
__version__ = package_version.version
del package_version




#----------------- General Function:  is_numeric_float -----------------

def is_numeric_float(*arrays):
    return True  #jfp

def jfp_was_is_numeric_float(*arrays):
    """Function to test whether a variable(s) is a Numeric floating
       point array (of any supported precision).

       If any of the input arrays are not Numeric arrays, or if any of 
       the input arrays are not floating, return false.  If all arrays 
       are floating and Numeric return true.

       "Floating" is defined as any one of the following Numeric 
       floating attributes:  Float, Float0, Float8, Float16, Float32, 
       Float64.

       Method Arguments:
       * *arrays:  Any number of array arguments.  All in the parameter
         list must be Numeric floating point arrays for function to 
         return true.

       Example:
       >>> import is_numeric_float
       >>> a = [1., 2., 3.]
       >>> print is_numeric_float.is_numeric_float(a)
       0
       >>> import Numeric as N
       >>> a = N.array([1., 2., 3.])
       >>> a.typecode()
       'd'
       >>> b = N.array([11., -52., 9., 39.])
       >>> print is_numeric_float.is_numeric_float(a,b)
       1
    """
    import numpy as N
    #jfp was import Numeric as N
    a_numeric_array = N.zeros(1)

    # If any of arrays is not Numeric, return false:
    for array in arrays:
        if type(array) != type(a_numeric_array):
            return 0

    # If any of arrays is not a version of float, return false:
    for array in arrays:
        is_float = 0

        if array.typecode() == N.Float:    is_float = 1
        if array.typecode() == N.Float0:   is_float = 1
        if array.typecode() == N.Float8:   is_float = 1
        if array.typecode() == N.Float16:  is_float = 1
        if array.typecode() == N.Float32:  is_float = 1
        if array.typecode() == N.Float64:  is_float = 1

        if is_float == 0:  return 0

    # Return true:
    return 1




#-------------------------- Main:  Test Module -------------------------

#- Define additional examples for doctest to use:

__test__ = { 'Additional Example 1':
    """
    >>> import is_numeric_float
    >>> import Numeric as N
    >>> a = N.array([1., 2., 3.])
    >>> b = N.array([10., -12, 12., 4., -9.])
    >>> c = N.array([-1., -8., 30., 31.])
    >>> print is_numeric_float.is_numeric_float(a,b,c)
    1
    >>> a = N.array([1., 2., 3.])
    >>> b = [1., 2., 3.]
    >>> print is_numeric_float.is_numeric_float(a,b)
    0
    >>> a = N.array([1., 2., 3.])
    >>> b = N.array([1, 2, 3])
    >>> print is_numeric_float.is_numeric_float(a,b)
    0
    """ }


#- Execute doctest if module is run from command line:

if __name__ == "__main__":
    """Test the module.

    Tests the examples in all the module documentation 
    strings, plus __test__.
    """
    import doctest, sys
    doctest.testmod(sys.modules[__name__])




# ===== end file =====
