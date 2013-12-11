#!/usr/bin/python -tt
#=======================================================================
#                        General Documentation

"""Module defines a single class.

   See class docstring for description.
"""

#-----------------------------------------------------------------------
#                       Additional Documentation
#
# RCS Revision Code:
#   $Id: atmconst.py,v 1.5 2004/07/16 18:27:27 jlin Exp $
#
# Modification History:
# - 13 Oct 2003:  Original by Johnny Lin, Computation Institute,
#   University of Chicago.  Passed passably reasonable tests.
# - 17 Jan 2004:  Changes to g.
# - 02 Mar 2004:  Change structure to include class and instance
#   attributes.  Add sea-level quantities.
# - 16 Jul 2004:  Add Stefan-Boltzman constant.  Small bug fix.
#
# Notes:
# - Written for Python 2.2.
# - No non-built-in packages and modules required.
#
# Copyright (c) 2003-2004 by Johnny Lin.  For licensing, distribution 
# conditions, contact information, and additional documentation see
# the URL http://www.johnny-lin.com/py_pkgs/atmqty/doc/.
#=======================================================================




#---------------- Module General Import and Declarations ---------------

#- Set module version number to package version number, etc.:

import package_version
__version__ = package_version.version
__author__  = package_version.author
__date__    = package_version.date
__credits__ = package_version.credits
del package_version




#----------------------- Class AtmConst:  Header -----------------------

class AtmConst:
    """Key atmospheric-related constants, defined for the earth.

    This class accepts no arguments and has no methods.  Class
    attributes set the atmospheric related constants.  A copy of all 
    class attributes (whether non-derived or derived) are made as 
    instance attributes to allow a straightforward way to alter a 
    constant locally without affecting the entire class.

    Remember, if you change a class attribute, the class attribute
    for all pre-existing instances of the class will change, and any 
    new instances of the class will be initialized to the value of
    the changed class attribute.


    Class Attributes:
    * c_p:  Specific heat at constant pressure for dry air [J/(K kg)].
    * C2K_add_offset:  Value to add to degrees Centigrade to convert 
      to Kelvin.  0 deg C is defined to be at the ice point, which is
      273.15 K.  Note the triple point and ice point are different.
      In Kelvin, the fundamental reference point is the triple point,
      which equals 273.16.  See Weast (p. F-73, 90) for details.
    * epsilon:  Ratio of gas constant for dry air to gas constant 
      for water vapor [unitless].
    * g:  Gravitational constant [m/s**2].  Set to g_wmo.
    * g_approx:  Approximate value of gravitational constant [m/s**2].
      This value is commonly used in rough calculations.
    * g_rean:  Gravitational constant [m/s**2] used in most calcula-
      tions in the NCEP/NCAR reanalysis.  See the FAQ for details:
      http://dss.ucar.edu/pub/reanalysis/FAQ.html.
    * g_wmo:  Gravitational constant [m/s**2] used by the WMO to cali-
      brate barometers.
    * Gamma_d:  Dry adiabatic lapse rate [K/m].
    * ice_point:  The ice point of water [K].
    * kappa:  Ratio R_d to c_p [unitless].
    * Omega:  Angular velocity of the Earth [rad/s].
    * R_d:  Gas constant for dry air [J/(K kg)].
    * R_univ:  Universal gas constant [J/(mol kg)].
    * R_v:  Gas constant for water vapor [J/(K kg)].
    * Rad_earth:  Mean radius of the earth [m].  Value used is the same
      as the shared constants value in the NCAR CCSM Coupler:
      http://www.ccsm.ucar.edu/models/ccsm2.0/cpl5/users_guide/node10.html.
      See the references section below for the citation of the coupler's
      User's Guide.
    * sea_level_press:  Sea level pressure [Pa].
    * sea_level_temp:  Sea level temperature [K].
    * sigma:  Stefan-Boltzman constant [W/(m**2 K**4)].
    * triple_point:  The triple point of water [K].


    Class Instance Attributes:
    * All the class attributes also exist as instance attributes of the
      same name.  Initial values of the instance attributes are set to 
      the value of the corresponding class attributes.


    References:
    * Carmichael, Ralph (2003):  "Definition of the 1976 Standard Atmo-
      sphere to 86 km," Public Domain Aeronautical Software (PDAS).
      URL:  http://www.pdas.com/coesa.htm.
    * Glickman, T. S. (Ed.) (2000):  Glossary of Meterology.  Boston,
      MA:  American Meteorology Society, 855 pp.
    * Kauffman, B. G., and W. G. Large (2002):  The CCSM Coupler, Ver-
      sion 5.0, Combined User's Guide, Source Code Reference, and Scien-
      tific Description.  Boulder, CO:  NCAR.  Available online at URL:
      http://www.ccsm.ucar.edu/models/ccsm2.0/cpl5/users_guide/.
    * Peixoto, J. P., and A. H. Oort (1992):  Physics of Climate.  
      New York, NY:  American Institute of Physics, ISBN 0-88318-711-6, 
      520 pp.
    * Shea, D. J., S. J. Worley, I. R. Stern, and T. J. Hoar (1995, 
      2003): An Introduction to Atmospheric and Oceanographic Datasets, 
      NCAR Technical Note NCAR/TN-404+IA.  Boulder, CO:  NCAR.  Web 
      copy:  http://www.cgd.ucar.edu/cas/tn404/.
    * Wallace, J. M., and P. V. Hobbs (1977): Atmospheric Science:  
      An Introductory Survey.  San Diego, CA:  Academic Press, ISBN 
      0-12-732950-1, 467 pp.
    * Weast, R. C. (Ed.) (1987):  CRC Handbook of Chemistry and Physics
      (68th Edition).  Boca Raton, FL:  CRC Press, Inc.


    Examples:
    >>> from atmconst import AtmConst
    >>> AtmConst.g
    9.8066499999999994
    >>> const = AtmConst()
    >>> const.g
    9.8066499999999994

    >>> const.g = AtmConst.g_rean
    >>> const.g
    9.8000000000000007
    >>> AtmConst.g
    9.8066499999999994
    >>> new_const = AtmConst()
    >>> new_const.g
    9.8066499999999994

    >>> AtmConst.g = AtmConst.g_rean
    >>> AtmConst.g
    9.8000000000000007
    >>> new_const.g
    9.8066499999999994
    >>> newest_const = AtmConst()
    >>> newest_const.g
    9.8000000000000007
    """

#------------------ Class AtmConst:  Class Attributes ------------------

    #- Non-derived constants:

    c_p = 1004.                # (Wallace & Hobbs, p. 69)
    g_approx = 9.81            # (Wallace & Hobbs, p. 68)
    g_rean = 9.8               # (see attribute description)
    g_wmo = 9.80665            # (Shea et al., Ch. 3)
    ice_point = 273.15         # (Weast, p. F-90)
    Omega = 7.2921e-5          # (Glickman, p. 42)
    R_d = 287.05               # (Garratt, p. 283)
    R_univ = 8.316963          # (Glickman, p. 328)
    R_v = 461.53               # (Garratt, p. 283)
    Rad_earth = 6.37122e+6     # (see attribute description)
    sea_level_press = 101325.  # (Carmichael)
    sea_level_temp = 288.15    # (Carmichael)
    sigma = 5.67032e-8         # (Weast, p. F-186)
    triple_point = 273.16      # (Weast, p. F-90)


    #- Derived constants:

    C2K_add_offset = ice_point
    epsilon = R_d / R_v
    g = g_wmo
    Gamma_d = g / c_p
    kappa = R_d / c_p




#----------------- Class AtmConst:  Instance Attributes ----------------

    def __init__(self):
        """Initialize copy of class attributes as instance attributes.
        """

        #- Class attribute was non-derived:

        self.c_p             = self.__class__.c_p
        self.g_approx        = self.__class__.g_approx
        self.g_rean          = self.__class__.g_rean
        self.g_wmo           = self.__class__.g_wmo
        self.ice_point       = self.__class__.ice_point
        self.Omega           = self.__class__.Omega
        self.R_d             = self.__class__.R_d
        self.R_univ          = self.__class__.R_univ
        self.R_v             = self.__class__.R_v
        self.Rad_earth       = self.__class__.Rad_earth
        self.sea_level_press = self.__class__.sea_level_press
        self.sea_level_temp  = self.__class__.sea_level_temp
        self.sigma           = self.__class__.sigma
        self.triple_point    = self.__class__.triple_point


        #- Class attribute was derived:

        self.C2K_add_offset = self.__class__.C2K_add_offset
        self.epsilon        = self.__class__.epsilon
        self.g              = self.__class__.g
        self.Gamma_d        = self.__class__.Gamma_d
        self.kappa          = self.__class__.kappa




#-------------------------- Main:  Test Module -------------------------

#- Define additional examples for doctest to use:

__test__ = { 'Additional Examples':
    """
    (1) Class Attributes:

    >>> from atmconst import AtmConst
    >>> AtmConst.c_p
    1004.0
    >>> (AtmConst.g_approx, AtmConst.g_rean, AtmConst.g_wmo)
    (9.8100000000000005, 9.8000000000000007, 9.8066499999999994)
    >>> (AtmConst.R_d, AtmConst.R_univ, AtmConst.R_v)
    (287.05000000000001, 8.3169629999999994, 461.52999999999997)
    >>> (AtmConst.Gamma_d, AtmConst.kappa, AtmConst.epsilon)
    (0.0097675796812748995, 0.28590637450199202, 0.62195306913960091)
    >>> (AtmConst.ice_point, AtmConst.triple_point, AtmConst.C2K_add_offset)
    (273.14999999999998, 273.16000000000003, 273.14999999999998)
    >>> (AtmConst.sea_level_press, AtmConst.sea_level_temp)
    (101325.0, 288.14999999999998)
    >>> AtmConst.Omega
    7.2921000000000002e-05
    >>> AtmConst.Rad_earth
    6371220.0
    >>> AtmConst.sigma
    5.6703199999999999e-08

    (2) Instance Attributes:

    >>> from atmconst import AtmConst
    >>> const = AtmConst()
    >>> const.c_p
    1004.0
    >>> (const.g_approx, const.g_rean, const.g_wmo)
    (9.8100000000000005, 9.8000000000000007, 9.8066499999999994)
    >>> (const.R_d, const.R_univ, const.R_v)
    (287.05000000000001, 8.3169629999999994, 461.52999999999997)
    >>> (const.Gamma_d, const.kappa, const.epsilon)
    (0.0097675796812748995, 0.28590637450199202, 0.62195306913960091)
    >>> (const.ice_point, const.triple_point, const.C2K_add_offset)
    (273.14999999999998, 273.16000000000003, 273.14999999999998)
    >>> (const.sea_level_press, const.sea_level_temp)
    (101325.0, 288.14999999999998)
    >>> const.Omega
    7.2921000000000002e-05
    >>> const.Rad_earth
    6371220.0
    >>> const.sigma
    5.6703199999999999e-08
    """ }


#- Execute doctest if module is run from command line:

if __name__ == "__main__":
    """Test the module.

    Tests the examples in all the module documentation strings, plus 
    __test__.

    To ensure that module testing of this module works, the parent 
    directory to the current directory is added to sys.path.
    """
    import doctest, sys, os
    sys.path.append(os.pardir)
    doctest.testmod(sys.modules[__name__])




# ===== end file =====
