#!/usr/local/uvcdat/1.3.1/bin/python -tt
# was #!/usr/bin/python -tt
#=======================================================================
#                        General Documentation

"""Single-function module.

   See function docstring for description.
"""

#-----------------------------------------------------------------------
#                       Additional Documentation
#
# RCS Revision Code:
#   $Id: press2alt.py,v 1.3 2004/03/13 00:37:16 jlin Exp $
#
# Modification History:
# - 12 Mar 2004:  Original by Johnny Lin, Computation Institute,
#   University of Chicago.  Passed reasonable tests.
#
# Notes:
# - Written for Python 2.2.
# - Module docstrings can be tested using the doctest module.  To
#   test, execute "python press2alt.py".  Replicates results from
#   IDL function press2alt by Dominik Brunner (see http://www.iac.
#   ethz.ch/~dominik/idltools/atmos_phys/press2alt.pro) to a mini-
#   mum of 6 significant figures (when the gravitational and gas
#   constants are (re-)defined to match the Brunner function).
# - Other atmqty modules required.  See import statements through-
#   out for other packages required.
#
# Copyright (c) 2004 by Johnny Lin.  For licensing, distribution 
# conditions, contact information, and additional documentation see
# the URL http://www.johnny-lin.com/py_pkgs/atmqty/doc/.
#=======================================================================




#---------------- Module General Import and Declarations ---------------

#- Set module version number etc. to package version number etc.:

import package_version
__version__ = package_version.version
__author__  = package_version.author
__date__    = package_version.date
__credits__ = package_version.credits \
   + '\n' \
   + 'Module inspired by the IDL function press2alt by Dominik Brunner;' \
   + '\n' \
   + 'see ' \
   + 'http://www.iac.ethz.ch/~dominik/idltools/atmos_phys/press2alt.pro.'
del package_version




#-------------- Private Function:  Pressure From Altitude --------------

def _pfromz_MA(z, lapse_rate, P_bott, T_bott, z_bott):
    """Pressure given altitude in a constant lapse rate layer.

    The dry gas constant is used in calculations requiring the gas
    constant.  See the docstring for press2alt for references.

    Input Arguments:
    * z:  Geopotential altitude [m].
    * lapse_rate:  -dT/dz [K/m] over the layer.
    * P_bott:  Pressure [hPa] at the base of the layer.
    * T_bott:  Temperature [K] at the base of the layer.
    * z_bott:  Geopotential altitude [m] of the base of the layer.

    Output:
    * Pressure [hPa] for each element given in the input arguments.

    All input arguments can be either a scalar or an MA array.  All 
    arguments that are MA arrays, however, are of the same size and 
    shape.  If every input argument is a scalar, the output is a scalar.  
    If any of the input arguments is an MA array, the output is an MA 
    array of the same size and shape.
    """
    #jfp was import Numeric as N
    import numpy as N
    #jfp was import MA
    import numpy.ma as MA
    from atmconst import AtmConst

    const = AtmConst()

    if MA.size(lapse_rate) == 1:
        #jfp was if MA.array(lapse_rate)[0] == 0.0:
        if MA.array(lapse_rate) == 0.0:
            return P_bott * \
                   MA.exp( -const.g / (const.R_d*T_bott) * (z-z_bott) )
        else:
            exponent = const.g / (const.R_d * lapse_rate)
            return P_bott * \
                   ( (1.0 - (lapse_rate * (z-z_bott) / T_bott))**exponent )
    else:
        exponent = const.g / (const.R_d * lapse_rate)
        P = P_bott * \
            ( (1.0 - (lapse_rate * (z-z_bott) / T_bott))**exponent )
        P_at_0 = P_bott * \
                 MA.exp( -const.g / (const.R_d*T_bott) * (z-z_bott) )

        zero_lapse_mask = MA.filled(MA.where(lapse_rate == 0., 1, 0), 0)
        zero_lapse_mask_indices_flat = N.nonzero(N.ravel(zero_lapse_mask))
        P_flat = MA.ravel(P)
        MA.put( P_flat, zero_lapse_mask_indices_flat \
              , MA.take(MA.ravel(P_at_0), zero_lapse_mask_indices_flat) )
        return MA.reshape(P_flat, P.shape)




#-------------- Private Function:  Altitude From Pressure --------------

def _zfromp_MA(P, lapse_rate, P_bott, T_bott, z_bott):
    """Altitude given pressure in a constant lapse rate layer.

    The dry gas constant is used in calculations requiring the gas
    constant.  See the docstring for press2alt for references.

    Input Arguments:
    * P:  Pressure [hPa].
    * lapse_rate:  -dT/dz [K/m] over the layer.
    * P_bott:  Pressure [hPa] at the base of the layer.
    * T_bott:  Temperature [K] at the base of the layer.
    * z_bott:  Geopotential altitude [m] of the base of the layer.

    Output:
    * Altitude [m] for each element given in the input arguments.

    All input arguments can be either a scalar or an MA array.  All 
    arguments that are MA arrays, however, are of the same size and 
    shape.  If every input argument is a scalar, the output is a scalar.
    If any of the input arguments is an MA array, the output is an MA 
    array of the same size and shape.
    """
    import numpy as N
    #jfp was import Numeric as N
    import numpy.ma as MA
    #jfp was import MA
    from atmconst import AtmConst

    const = AtmConst()

    if MA.size(lapse_rate) == 1:
        if MA.array(lapse_rate)[0] == 0.0:
            return ( (-const.R_d * T_bott / const.g) * MA.log(P/P_bott) ) + \
                   z_bott
        else:
            exponent = (const.R_d * lapse_rate) / const.g
            return ((T_bott / lapse_rate) * (1. - (P/P_bott)**exponent)) + \
                   z_bott
    else:
        exponent = (const.R_d * lapse_rate) / const.g
        z = ((T_bott / lapse_rate) * (1. - (P/P_bott)**exponent)) + z_bott
        z_at_0 = ( (-const.R_d * T_bott / const.g) * MA.log(P/P_bott) ) + \
                 z_bott

        zero_lapse_mask = MA.filled(MA.where(lapse_rate == 0., 1, 0), 0)
        zero_lapse_mask_indices_flat = N.nonzero(N.ravel(zero_lapse_mask))
        z_flat = MA.ravel(z)
        MA.put( z_flat, zero_lapse_mask_indices_flat \
              , MA.take(MA.ravel(z_at_0), zero_lapse_mask_indices_flat) )
        return MA.reshape(z_flat, z.shape)




#-------------------------- General Function ---------------------------

def press2alt(arg, P0=None, T0=None, missing=1e+20, invert=0):
    """Calculate elevation given pressure (or vice versa).

    Calculations are made assuming that the temperature distribution
    follows the 1976 Standard Atmosphere.  Technically the standard
    atmosphere defines temperature distribution as a function of
    geopotential altitude, and this routine actually calculates geo-
    potential altitude rather than geometric altitude.


    Method Positional Argument:
    * arg:  Numeric floating point vector of any shape and size, or a
      Numeric floating point scalar.  If invert=0 (the default), arg 
      is air pressure [hPa].  If invert=1, arg is elevation [m].


    Method Keyword Arguments:
    * P0:  Pressure [hPa] at the surface (altitude equals 0).  Numeric 
      floating point vector of same size and shape as arg or a scalar.
      Default of keyword is set to None, in which case the routine 
      uses the value of instance attribute sea_level_press (converted
      to hPa) from the AtmConst class.  Keyword value is used if the 
      keyword is set in the function call.  This keyword cannot have 
      any missing values.

    * T0:  Temperature [K] at the surface (altitude equals 0).  Numeric 
      floating point vector of same size and shape as arg or a scalar.  
      Default of keyword is set to None, in which case the routine uses 
      the value of instance attribute sea_level_temp from the AtmConst
      class.  Keyword value is used if the keyword is set in the func-
      tion call.  This keyword cannot have any missing values.

    * missing:  If arg has missing values, this is the missing value 
      value.  Floating point scalar.  Default is 1e+20.

    * invert:  If set to 1, function calculates pressure [hPa] from 
      altitude [m].  In that case, positional input variable arg is 
      altitude [m] and the output is pressure [hPa].  Default value of 
      invert=0, which means the function calculates altitude given 
      pressure.


    Output:
    * If invert=0 (the default), output is elevation [m] at each 
      element of arg, relative to the surface.  If invert=1, output
      is the air pressure [hPa].  Numeric floating point array of 
      the same size and shape as arg.

      If there are any missing values in output, those values are set 
      to the value in argument missing from the input.  If there are 
      missing values in the output due to math errors and missing is 
      set to None, output will fill those missing values with the MA 
      default value of 1e+20.


    References:
    * Carmichael, Ralph (2003):  "Definition of the 1976 Standard Atmo-
      sphere to 86 km," Public Domain Aeronautical Software (PDAS).
      URL:  http://www.pdas.com/coesa.htm.

    * Wallace, J. M., and P. V. Hobbs (1977): Atmospheric Science:
      An Introductory Survey.  San Diego, CA:  Academic Press, ISBN
      0-12-732950-1, pp. 60-61.


    Examples:

    (1) Calculating altitude given pressure:

    >>> from press2alt import press2alt
    >>> import Numeric as N
    >>> press = N.array([200., 350., 850., 1e+20, 50.])
    >>> alt = press2alt(press, missing=1e+20)
    >>> ['%.7g' % alt[i] for i in range(5)]
    ['11783.94', '8117.19', '1457.285', '1e+20', '20575.96']

    (2) Calculating pressure given altitude:

    >>> alt = N.array([0., 10000., 15000., 20000., 50000.])
    >>> press = press2alt(alt, missing=1e+20, invert=1)
    >>> ['%.7g' % press[i] for i in range(5)]
    ['1013.25', '264.3589', '120.443', '54.74718', '0.7593892']

    (3) Input is a Numeric floating point scalar, and using a keyword
        set surface pressure to a different scalar:

    >>> alt = press2alt(N.array(850.), P0=1000.)
    >>> ['%.7g' % alt[0]]
    ['1349.778']
    """
    import numpy as N
    import numpy.ma as MA
    #jfp was import MA
    #jfp was import Numeric as N
    from atmconst import AtmConst
    from is_numeric_float import is_numeric_float


    #- Check input is of the correct type:

    if is_numeric_float(arg) != 1:
        raise TypeError, "press2alt:  Arg not Numeric floating"


    #- Import general constants and set additional constants.  h1_std
    #  is the lower limit of the Standard Atmosphere layer geopoten-
    #  tial altitude [m], h2_std is the upper limit [m] of the layer,
    #  and dT/dh is the temperature gradient (i.e. negative of the
    #  lapse rate) [K/m]:

    const = AtmConst()

    h1_std   = N.array([0., 11., 20., 32., 47., 51., 71.]) * 1000.
    h2_std   = N.array( MA.concatenate([h1_std[1:], [84.852*1000.]]) )
    dTdh_std = N.array([-6.5, 0.0, 1.0, 2.8, 0.0, -2.8, -2.0]) / 1000.


    #- Prep arrays for masked array calculation and set conditions
    #  at sea-level.  Pressures are in hPa and temperatures in K.
    #  Sea-level conditions arrays are same shape/size as P_or_z.
    #  If input argument is a scalar, make the local variable used
    #  for calculations a 1-element vector:

    if missing == None: P_or_z = MA.masked_array(arg)
    else:               P_or_z = MA.masked_values(arg, missing, copy=0)

    if P_or_z.shape == ():
        P_or_z = MA.reshape(P_or_z, (1,))

    if P0 == None:
        #jfp was P0_use = MA.zeros(P_or_z.shape, typecode=MA.Float) \
        P0_use = MA.zeros(P_or_z.shape) \
               + (const.sea_level_press / 100.)
    else:
        #jfp was P0_use = MA.zeros(P_or_z.shape, typecode=MA.Float) \
        P0_use = MA.zeros(P_or_z.shape) \
               + MA.masked_array(P0)

    if T0 == None:
        #jfp was T0_use = MA.zeros(P_or_z.shape, typecode=MA.Float) \
        T0_use = MA.zeros(P_or_z.shape) \
               + const.sea_level_temp
    else:
        #jfp was T0_use = MA.zeros(P_or_z.shape, typecode=MA.Float) \
        T0_use = MA.zeros(P_or_z.shape) \
               + MA.masked_array(T0)


    #- Calculate P and T for the boundaries of the 7 layers of the
    #  Standard Atmosphere for the given P0 and T0 (layer 0 goes from
    #  P0 to P1, layer 1 from P1 to P2, etc.).  These are given as
    #  8 element dictionaries P_std and T_std where the key is the
    #  location (P_std[0] is at the bottom of layer 0, P_std[1] is the
    #  top of layer 0 and bottom of layer 1, ... and P_std[7] is the
    #  top of layer 6).  Remember P_std and T_std are dictionaries but
    #  dTdh_std, h1_std, and h2_std are vectors:

    P_std = {0:P0_use}
    T_std = {0:T0_use}

    for i in range(len(h1_std)):
        P_std[i+1] = _pfromz_MA( h2_std[i], -dTdh_std[i] \
                               , P_std[i], T_std[i], h1_std[i] )
        T_std[i+1] = T_std[i] + ( dTdh_std[i] * (h2_std[i]-h1_std[i]) )

    #- Test input is within Standard Atmosphere limits:

    if invert == 0:
        tmp = MA.where(P_or_z < P_std[len(h1_std)], 1, 0)
        if MA.sum(MA.ravel(tmp)) > 0:
            raise ValueError, "press2alt:  Pressure out-of-range"
    else:
        tmp = MA.where(P_or_z > MA.maximum(h2_std), 1, 0)
        if MA.sum(MA.ravel(tmp)) > 0:
            raise ValueError, "press2alt:  Altitude out-of-range"


    #- What layer number is each element of P_or_z in?

    P_or_z_layer = MA.zeros(P_or_z.shape)

    if invert == 0:
        for i in range(len(h1_std)):
            tmp = MA.where( MA.logical_and( (P_or_z <= P_std[i]) \
                                          , (P_or_z >  P_std[i+1]) ) \
                          , i, 0 )
            P_or_z_layer += tmp
    else:
        for i in range(len(h1_std)):
            tmp = MA.where( MA.logical_and( (P_or_z >= h1_std[i]) \
                                          , (P_or_z <  h2_std[i]) ) \
                          , i, 0 )
            P_or_z_layer += tmp


    #- Fill in the bottom-of-the-layer variables and the lapse rate
    #  for the layers that the levels are in.  The *_actual variables 
    #  are the values of dTdh, P_bott, etc. for each element in the
    #  P_or_z_flat array:

    P_or_z_flat = MA.ravel(P_or_z)
    P_or_z_flat_mask = P_or_z_flat.mask
    if P_or_z_flat.mask==False:
        P_or_z_flat_mask = MA.make_mask_none(P_or_z_flat.shape)
    #jfp was:
    #if P_or_z_flat.mask() == None:
    #    P_or_z_flat_mask = MA.make_mask_none(P_or_z_flat.shape)
    #else:
    #    P_or_z_flat_mask = P_or_z_flat.mask()

    P_or_z_layer_flat = MA.ravel(P_or_z_layer)
    #jfp was dTdh_actual       = MA.zeros(P_or_z_flat.shape, typecode=MA.Float)
    #jfp was P_bott_actual     = MA.zeros(P_or_z_flat.shape, typecode=MA.Float)
    #jfp was T_bott_actual     = MA.zeros(P_or_z_flat.shape, typecode=MA.Float)
    #jfp was z_bott_actual     = MA.zeros(P_or_z_flat.shape, typecode=MA.Float)
    dTdh_actual       = MA.zeros(P_or_z_flat.shape)
    P_bott_actual     = MA.zeros(P_or_z_flat.shape)
    T_bott_actual     = MA.zeros(P_or_z_flat.shape)
    z_bott_actual     = MA.zeros(P_or_z_flat.shape)

    for i in xrange(MA.size(P_or_z_flat)):
        if P_or_z_flat_mask[i] != 1:
            layer_number     = P_or_z_layer_flat[i]
            dTdh_actual[i]   = dTdh_std[layer_number]
            P_bott_actual[i] = MA.ravel(P_std[layer_number])[i]
            T_bott_actual[i] = MA.ravel(T_std[layer_number])[i]
            z_bott_actual[i] = h1_std[layer_number]
        else:
            dTdh_actual[i]   = MA.masked
            P_bott_actual[i] = MA.masked
            T_bott_actual[i] = MA.masked
            z_bott_actual[i] = MA.masked


    #- Calculate pressure/altitude from altitude/pressure (output is
    #  a flat array):
    
    if invert == 0:
        output = _zfromp_MA( P_or_z_flat, -dTdh_actual \
                           , P_bott_actual, T_bott_actual, z_bott_actual )
    else:
        output = _pfromz_MA( P_or_z_flat, -dTdh_actual \
                           , P_bott_actual, T_bott_actual, z_bott_actual )


    #- Return output as same shape as input positional argument:

    return MA.filled( MA.reshape(output, arg.shape), missing )




#-------------------------- Main:  Test Module -------------------------

#- Define additional examples for doctest to use:

__test__ = {'Additional Examples':
    """
    (1) Pressures at the Standard Atmosphere level boundaries.  These
        values should be almost identical (with allowance for floating
        point precision differences) with the output found at this web
        site:  http://www.pdas.com/pressure.htm.

    >>> from press2alt import press2alt
    >>> import Numeric as N
    >>> alt = N.array([0., 11., 20., 32., 47., 51., 71., 84.8519]) * 1000.
    >>> normP = press2alt(alt, invert=1) / 1013.25
    >>> ['%.7f' % normP[i] for i in range(5)]
    ['1.0000000', '0.2233575', '0.0540313', '0.0085662', '0.0010945']
    >>> ['%.7e' % normP[i] for i in range(5,8)]
    ['6.6058355e-04', '3.9042592e-05', '3.6845835e-06']

    (2) Different P0 (as vectors):

    >>> press = N.array([890., 900., 10.])
    >>> P0 = N.array([1000., 1010., 1011.])
    >>> alt = press2alt(press, P0=P0)
    >>> ['%.7f' % alt[i] for i in range(3)]
    ['972.0795462', '961.9895123', '31039.4906986']

    (3) Different P0 and T0 (as vectors):

    >>> press = N.array([890., 900., 10.])
    >>> P0 = N.array([1000., 1010., 1011.])
    >>> T0 = N.array([280., 270., 290.])
    >>> alt = press2alt(press, P0=P0, T0=T0)
    >>> ['%.7f' % alt[i] for i in range(3)]
    ['944.5853650', '901.3956909', '31288.8783167']

    (4) Check above input not changed:

    >>> press.shape
    (3,)
    >>> alt.shape
    (3,)
    >>> ['%.7f' % press[i] for i in range(3)]
    ['890.0000000', '900.0000000', '10.0000000']
    >>> P0.shape
    (3,)
    >>> T0.shape
    (3,)
    >>> ['%.7f' % P0[i] for i in range(3)]
    ['1000.0000000', '1010.0000000', '1011.0000000']
    >>> ['%.7f' % T0[i] for i in range(3)]
    ['280.0000000', '270.0000000', '290.0000000']

    (5) Check for pressures and altitudes out of range and bad input:

    >>> alt = press2alt(N.array([850., 0.000001]))
    Traceback (most recent call last):
        ...
    ValueError: press2alt:  Pressure out-of-range
    >>> press = press2alt(N.array([11000., 100000]), invert=1)
    Traceback (most recent call last):
        ...
    ValueError: press2alt:  Altitude out-of-range
    >>> press = press2alt(11000., invert=1)
    Traceback (most recent call last):
        ...
    TypeError: press2alt:  Arg not Numeric floating

    (6) Tests with one-element input:

    >>> alt = press2alt(N.array(200.))
    >>> ['%.7g' % alt[0]]
    ['11783.94']
    >>> alt = press2alt(N.array([200.]))
    >>> ['%.7g' % alt[0]]
    ['11783.94']
    >>> press = press2alt(N.array(10000.), invert=1)
    >>> ['%.7g' % press[0]]
    ['264.3589']
    >>> press.shape
    ()
    >>> press = press2alt(N.array([10000.]), invert=1)
    >>> ['%.7g' % press[0]]
    ['264.3589']
    >>> press.shape
    (1,)
    """}


#- Execute doctest if module is run from command line:

if __name__ == "__main__":
    """Test the module.

    Tests the examples in all the module documentation strings, plus
    __test__.

    Note:  To help ensure that module testing of this file works, the
    parent directory to the current directory is added to sys.path.
    """
    import doctest, sys, os
    sys.path.append(os.pardir)
    doctest.testmod(sys.modules[__name__])




# ===== end file =====
