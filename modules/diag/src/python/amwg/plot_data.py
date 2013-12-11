#!/usr/local/uvcdat/2013-08-20/bin/python

# High-level function to set up data suitable for plotting.
# There's a whole lot left to do!

import cdms2, math
from metrics.fileio.filetable import *
from metrics.fileio.findfiles import *
from metrics.computation.reductions import *
from metrics.computation.plotspec import *
from metrics.amwg.derivations.oaht import *
from metrics.amwg.derivations.ncl_isms import *
from metrics.amwg.derivations.vertical import *
from pprint import pprint


def test_driver( path1, path2=None, filt2=None ):
    """ Test driver for setting up data for plots"""

    # First, find and index the data files.
    datafiles1 = dirtree_datafiles( path1 )
    print "jfp datafiles1=",datafiles1
    datafiles2 = dirtree_datafiles( path2, filt2 )
    print "jfp datafiles2=",datafiles2
    filetable1 = basic_filetable( datafiles1 )
    filetable2 = basic_filetable( datafiles2 )

    # Next we'll compute reduced variables.  They have generally been reduced by averaging in time,
    # and often more axes as well.  Reducing the data first is the fastest way to compute, important
    # if we need to be interactive.  And it is correct if whatever we plot is linear in the
    # variables, as is almost always the case.  But if we want to plot a highly nonlinear function
    # of the data variables, the averaging will have to wait until later.

    # The reduced_variables dict names and contains all the reduced variables which we have defined.
    # They will be used in defining instances of plotspec.
    reduced_variables = {
        'hyam_1': reduced_variable(
            variableid='hyam', filetable=filetable1,
            reduction_function=(lambda x,vid=None: x) ),
        'hybm_1': reduced_variable(
            variableid='hybm', filetable=filetable1,
            reduction_function=(lambda x,vid=None: x) ),
        'PS_ANN_1': reduced_variable(
            variableid='PS', filetable=filetable1,
            reduction_function=reduce2lat ),
        'T_CAM_ANN_1': reduced_variable(
            variableid='T', filetable=filetable1,
            reduction_function=reduce2levlat ),
        'T_CAM_ANN_2': reduced_variable(
            variableid='T', filetable=filetable2,
            reduction_function=reduce2levlat ),
        'TREFHT_ANN_latlon_Npole_1': reduced_variable(
            variableid='TREFHT', filetable=filetable1,
            reduction_function=(lambda x,vid=None: restrict_lat(reduce2latlon(x,vid=vid),50,90)) ),
        'TREFHT_ANN_latlon_Npole_2': reduced_variable(
            variableid='TREFHT', filetable=filetable2,
            reduction_function=(lambda x,vid=None: restrict_lat(reduce2latlon(x,vid=vid),50,90)) ),
        'TREFHT_ANN_lat_1': reduced_variable(
            variableid='TREFHT', filetable=filetable1,
            reduction_function=reduce2lat ),
        'TREFHT_DJF_lat_1': reduced_variable(
            variableid='TREFHT',
            filetable=filetable1,
            reduction_function=(lambda x,vid=None: reduce2lat_seasonal(x,seasonsDJF,vid=vid)) ),
        'TREFHT_DJF_lat_2': reduced_variable(
            variableid='TREFHT',
            filetable=filetable2,
            reduction_function=(lambda x,vid=None: reduce2lat_seasonal(x,seasonsDJF,vid=vid)) ),
        'TREFHT_DJF_latlon_1': reduced_variable(
            variableid='TREFHT',
            filetable=filetable1,
            reduction_function=(lambda x,vid=None: reduce2latlon_seasonal(x,seasonsDJF,vid=vid)) ),
        'TREFHT_DJF_latlon_2': reduced_variable(
            variableid='TREFHT',
            filetable=filetable2,
            reduction_function=(lambda x,vid=None: reduce2latlon_seasonal(x,seasonsDJF,vid=vid)) ),
        'TREFHT_JJA': reduced_variable(
            variableid='TREFHT',
            filetable=filetable1,
            reduction_function=(lambda x,vid=None: reduce2lat_seasonal(x,seasonsJJA,vid=vid)) ),
        'PRECT_JJA_lat_1': reduced_variable(
            variableid='PRECT',
            filetable=filetable1,
            reduction_function=(lambda x,vid=None: reduce2lat_seasonal(x,seasonsJJA,vid=vid)) ),
        'PRECT_JJA_lat_2': reduced_variable(
            variableid='PRECT',
            filetable=filetable2,
            reduction_function=(lambda x,vid=None: reduce2lat_seasonal(x,seasonsJJA,vid=vid)) ),


        # CAM variables needed for heat transport:
            # FSNS, FLNS, FLUT, FSNTOA, FLNT, FSNT, SHFLX, LHFLX,
        'FSNS_1': reduced_variable(
            variableid='FSNS',filetable=filetable1,reduction_function=(lambda x,vid:x) ),
        'FSNS_ANN_latlon_1': reduced_variable(
            variableid='FSNS',
            filetable=filetable1,
            reduction_function=reduce2latlon ),
        'FLNS_1': reduced_variable(
            variableid='FLNS',filetable=filetable1,reduction_function=(lambda x,vid:x) ),
        'FLNS_ANN_latlon_1': reduced_variable(
            variableid='FLNS',
            filetable=filetable1,
            reduction_function=reduce2latlon ),
        'FLUT_ANN_latlon_1': reduced_variable(
            variableid='FLUT',
            filetable=filetable1,
            reduction_function=reduce2latlon ),
        'FSNTOA_ANN_latlon_1': reduced_variable(
            variableid='FSNTOA',
            filetable=filetable1,
            reduction_function=reduce2latlon ),
        'FLNT_1': reduced_variable(
            variableid='FLNT',filetable=filetable1,reduction_function=(lambda x,vid:x) ),
        'FLNT_ANN_latlon_1': reduced_variable(
            variableid='FLNT',
            filetable=filetable1,
            reduction_function=reduce2latlon ),
        'FSNT_1': reduced_variable(
            variableid='FSNT',filetable=filetable1,reduction_function=(lambda x,vid:x) ),
        'FSNT_ANN_latlon_1': reduced_variable(
            variableid='FSNT',
            filetable=filetable1,
            reduction_function=reduce2latlon ),
        'QFLX_1': reduced_variable(
            variableid='QFLX',filetable=filetable1,reduction_function=(lambda x,vid:x) ),
        'SHFLX_1': reduced_variable(
            variableid='SHFLX',filetable=filetable1,reduction_function=(lambda x,vid:x) ),
        'SHFLX_ANN_latlon_1': reduced_variable(
            variableid='SHFLX',
            filetable=filetable1,
            reduction_function=reduce2latlon ),
        'LHFLX_ANN_latlon_1': reduced_variable(
            variableid='LHFLX',
            filetable=filetable1,
            reduction_function=reduce2latlon ),
        'ORO_ANN_latlon_1': reduced_variable(
            variableid='ORO',
            filetable=filetable1,
            reduction_function=reduce2latlon ),
        'OCNFRAC_ANN_latlon_1': reduced_variable(
            variableid='OCNFRAC',
            filetable=filetable1,
            reduction_function=reduce2latlon ),


        'ts_lat_old': reduced_variable(
            variableid='surface_temperature', # normally a CF standard_name, even for non-CF data.
            filetable=filetable1,
            reduction_function=reduce2lat_old ),
        'ts_lat_new': reduced_variable(
            variableid='surface_temperature', # normally a CF standard_name, even for non-CF data.
            filetable=filetable1,
            reduction_function=reduce2lat 
            # The reduction function will take just one argument, a variable (MV).  But it might
            # be expressed here as a lambda wrapping a more general function.
            # Often there will be ranges in time, space, etc. specified here.  No range means
            # everything.
            ),
        'ts_scalar_tropical_o': reduced_variable(
            variableid = 'surface_temperature',
            filetable=filetable1,
            reduction_function=(lambda mv,vid=None: reduce2scalar_zonal_old(mv,-20,20,vid=vid))
            ),
        'ts_scalar_tropical_n': reduced_variable(
            variableid = 'surface_temperature',
            filetable=filetable1,
            reduction_function=(lambda mv,vid=None: reduce2scalar_zonal(mv,-20,20,vid=vid))
            )
        }

    # Derived variables have to be treated separately from reduced variables
    # because derived variables generally depend on reduced variables.
    # But N.B.: the dicts reduced_variables and derived_variables
    # must never use the same key!
    derived_variables = {
        'CAM_HEAT_TRANSPORT_ALL_1': derived_var(
            vid='CAM_HEAT_TRANSPORT_ALL_1',
            inputs=['FSNS_ANN_latlon_1', 'FLNS_ANN_latlon_1', 'FLUT_ANN_latlon_1',
                    'FSNTOA_ANN_latlon_1', 'FLNT_ANN_latlon_1', 'FSNT_ANN_latlon_1',
                    'SHFLX_ANN_latlon_1', 'LHFLX_ANN_latlon_1', 'OCNFRAC_ANN_latlon_1' ],
            outputs=['atlantic_heat_transport','pacific_heat_transport',
                     'indian_heat_transport', 'global_heat_transport' ],
            func=oceanic_heat_transport ),
        'NCEP_OBS_HEAT_TRANSPORT_ALL_2': derived_var(
            vid='NCEP_OBS_HEAT_TRANSPORT_ALL_2',
            inputs=[],
            outputs=('latitude', ['atlantic_heat_transport','pacific_heat_transport',
                     'indian_heat_transport', 'global_heat_transport' ]),
            func=(lambda: ncep_ocean_heat_transport(path2) ) ),
        'T_ANN_1': derived_var(
            vid='T_ANN_1', inputs=['T_CAM_ANN_1', 'hyam_1', 'hybm_1', 'PS_ANN_1', 'T_CAM_ANN_2'],
            outputs=('temperature'),
            func=verticalize )
        }

    plotvars = dict( reduced_variables.items() + derived_variables.items() )

    # The plotvspecs dict names and contains all plotspec objects which we have defined.
    # The plotspeckeys variable, below, names the ones for which we will generate output.
    # A dict value can be a plotspec object, or a list of such objects.  A list of
    # plotspec instances specifies a page containing multiple plots in separate panes.
    plotspecs = {
        'TREFHT_ANN_Npole_ALL':
            ['TREFHT_ANN_Npole_1', 'TREFHT_ANN_Npole_2', 'TREFHT_ANN_Npole_diff'],
        'TREFHT_ANN_Npole_1': plotspec(
            vid='TREFHT_ANN_Npole_1',
            xvars=['TREFHT_ANN_latlon_Npole_1'], xfunc = lonvar,
            yvars=['TREFHT_ANN_latlon_Npole_1'], yfunc = latvar,
            zvars=['TREFHT_ANN_latlon_Npole_1'], zfunc = (lambda z: z),
            plottype='polar contour plot' ),
        'TREFHT_ANN_Npole_2': plotspec(
            vid='TREFHT_ANN_Npole_2',
            xvars=['TREFHT_ANN_latlon_Npole_2'], xfunc = lonvar,
            yvars=['TREFHT_ANN_latlon_Npole_2'], yfunc = latvar,
            zvars=['TREFHT_ANN_latlon_Npole_2'], zfunc = (lambda z: z),
            plottype='polar contour plot' ),
        'TREFHT_ANN_Npole_diff': plotspec(
            vid='TREFHT_ANN_Npole_diff',
            xvars=['TREFHT_ANN_latlon_Npole_1','TREFHT_ANN_latlon_Npole_2'], xfunc = lonvar_min,
            yvars=['TREFHT_ANN_latlon_Npole_1','TREFHT_ANN_latlon_Npole_2'], yfunc = latvar_min,
            zvars=['TREFHT_ANN_latlon_Npole_1','TREFHT_ANN_latlon_Npole_2'], zfunc = aminusb_2ax,
            plottype='polar contour plot' ),
        'TREFHT_DJF_laton_ALL':
            ['TREFHT_DJF_latlon_1', 'TREFHT_DJF_latlon_2', 'TREFHT_DJF_latlon_diff'],
        'TREFHT_DJF_latlon_1': plotspec(
            vid='TREFHT_DJF_latlon_1',
            xvars=['TREFHT_DJF_latlon_1'], xfunc = lonvar,
            yvars=['TREFHT_DJF_latlon_1'], yfunc = latvar,
            zvars=['TREFHT_DJF_latlon_1'], zfunc = (lambda z: z),
            plottype='contour plot' ),
        'TREFHT_DJF_latlon_2': plotspec(
            vid='TREFHT_DJF_latlon_2',
            xvars=['TREFHT_DJF_latlon_2'], xfunc = lonvar,
            yvars=['TREFHT_DJF_latlon_2'], yfunc = latvar,
            zvars=['TREFHT_DJF_latlon_2'], zfunc = (lambda z: z),
            plottype='contour plot' ),
        'TREFHT_DJF_latlon_diff': plotspec(
            vid='TREFHT_DJF_latlon_diff',
            xvars=['TREFHT_DJF_latlon_1','TREFHT_DJF_latlon_2'], xfunc=lonvar_min,
            yvars=['TREFHT_DJF_latlon_1','TREFHT_DJF_latlon_2'], yfunc=latvar_min,
            zvars=['TREFHT_DJF_latlon_1','TREFHT_DJF_latlon_2'], zfunc= aminusb_2ax,
            plottype='contour_plot'
            ),
        'T_ANN_VERT_CAM_OBS_ALL':
            ['T_VERT_ANN_1', 'T_VERT_ANN_2', 'T_VERT_difference' ],
        'T_VERT_difference': plotspec(
            vid='T_VERT_difference', xvars=['T_ANN_1','T_CAM_ANN_2'], xfunc = latvar_min,
            yvars=['T_ANN_1','T_CAM_ANN_2'], yfunc = levvar_min,
            ya1vars=['T_ANN_1','T_CAM_ANN_2'], ya1func = (lambda y1,y2: heightvar(levvar_min(y1,y2))),
            zvars=['T_ANN_1','T_CAM_ANN_2'], zfunc=aminusb_ax2, plottype="contour plot" ),
        'T_VERT_ANN_2': plotspec(
            vid='T_ANN_2', xvars=['T_CAM_ANN_2'], xfunc=latvar,
            yvars=['T_CAM_ANN_2'], yfunc=levvar, ya1vars=['T_CAM_ANN_2'], ya1func=heightvar,
            zvars=['T_CAM_ANN_2'], plottype='contour plot',
            zrangevars=['T_ANN_1','T_CAM_ANN_2'], zrangefunc=minmin_maxmax ),
        'T_VERT_ANN_1': plotspec(
            vid='T_ANN_1', xvars=['T_ANN_1'], xfunc=latvar,
            yvars=['T_ANN_1'], yfunc=levvar, ya1vars=['T_ANN_1'], ya1func=heightvar,
            zvars=['T_ANN_1'], plottype='contour plot',
            zrangevars=['T_ANN_1','T_CAM_ANN_2'], zrangefunc=minmin_maxmax ),
        'NCEP_OBS_HEAT_TRANSPORT_GLOBAL_2': plotspec(
            vid='NCEP_OBS_HEAT_TRANSPORT_GLOBAL_2',
            xvars=['NCEP_OBS_HEAT_TRANSPORT_ALL_2'], xfunc=(lambda x: x[0]),
            yvars=['NCEP_OBS_HEAT_TRANSPORT_ALL_2' ],
            yfunc=(lambda y: y[1][3]), plottype='line plot'),
        'NCEP_OBS_HEAT_TRANSPORT_PACIFIC_2': plotspec(
            vid='NCEP_OBS_HEAT_TRANSPORT_PACIFIC_2',
            xvars=['NCEP_OBS_HEAT_TRANSPORT_ALL_2'], xfunc=(lambda x: x[0]),
            yvars=['NCEP_OBS_HEAT_TRANSPORT_ALL_2' ],
            yfunc=(lambda y: y[1][0]), plottype='line plot'),
        'NCEP_OBS_HEAT_TRANSPORT_ATLANTIC_2': plotspec(
            vid='NCEP_OBS_HEAT_TRANSPORT_ATLANTIC_2',
            xvars=['NCEP_OBS_HEAT_TRANSPORT_ALL_2'], xfunc=(lambda x: x[0]),
            yvars=['NCEP_OBS_HEAT_TRANSPORT_ALL_2' ],
            yfunc=(lambda y: y[1][1]), plottype='line plot'),
        'NCEP_OBS_HEAT_TRANSPORT_INDIAN_2': plotspec(
            vid='NCEP_OBS_HEAT_TRANSPORT_INDIAN_2',
            xvars=['NCEP_OBS_HEAT_TRANSPORT_ALL_2'], xfunc=(lambda x: x[0]),
            yvars=['NCEP_OBS_HEAT_TRANSPORT_ALL_2' ],
            yfunc=(lambda y: y[1][2]), plottype='line plot'),
        'CAM_HEAT_TRANSPORT_GLOBAL_1': plotspec(
            vid='CAM_HEAT_TRANSPORT_GLOBAL_1',
            xvars=['FSNS_ANN_latlon_1'], xfunc=latvar,
            yvars=['CAM_HEAT_TRANSPORT_ALL_1' ],
            yfunc=(lambda y: y[3]), plottype='line plot'),
        'CAM_HEAT_TRANSPORT_PACIFIC_1': plotspec(
            vid='CAM_HEAT_TRANSPORT_PACIFIC_1',
            xvars=['FSNS_ANN_latlon_1'], xfunc=latvar,
            yvars=['CAM_HEAT_TRANSPORT_ALL_1' ],
            yfunc=(lambda y: y[0]), plottype='line plot'),
        'CAM_HEAT_TRANSPORT_ATLANTIC_1': plotspec(
            vid='CAM_HEAT_TRANSPORT_ATLANTIC_1',
            xvars=['FSNS_ANN_latlon_1'], xfunc=latvar,
            yvars=['CAM_HEAT_TRANSPORT_ALL_1' ],
            yfunc=(lambda y: y[1]), plottype='line plot'),
        'CAM_HEAT_TRANSPORT_INDIAN_1': plotspec(
            vid='CAM_HEAT_TRANSPORT_INDIAN_1',
            xvars=['FSNS_ANN_latlon_1'], xfunc=latvar,
            yvars=['CAM_HEAT_TRANSPORT_ALL_1' ],
            yfunc=(lambda y: y[2]), plottype='line plot'),
        'CAM_HEAT_TRANSPORT_ALL_1':
            ['CAM_HEAT_TRANSPORT_GLOBAL_1','CAM_HEAT_TRANSPORT_PACIFIC_1',
             'CAM_HEAT_TRANSPORT_ATLANTIC_1','CAM_HEAT_TRANSPORT_INDIAN_1'],
        'CAM_NCEP_HEAT_TRANSPORT_GLOBAL': plotspec(
            vid='CAM_NCEP_HEAT_TRANSPORT_GLOBAL',
            x1vars=['FSNS_ANN_latlon_1'], x1func=latvar,
            y1vars=['CAM_HEAT_TRANSPORT_ALL_1' ],
            y1func=(lambda y: y[3]),
            x2vars=['NCEP_OBS_HEAT_TRANSPORT_ALL_2'], x2func=(lambda x: x[0]),
            y2vars=['NCEP_OBS_HEAT_TRANSPORT_ALL_2' ],
            y2func=(lambda y: y[1][3]),
            plottype='2 line plot'  ),
        'CAM_NCEP_HEAT_TRANSPORT_PACIFIC': plotspec(
            vid='CAM_NCEP_HEAT_TRANSPORT_PACIFIC',
            x1vars=['FSNS_ANN_latlon_1'], x1func=latvar,
            y1vars=['CAM_HEAT_TRANSPORT_ALL_1' ],
            y1func=(lambda y: y[0]),
            x2vars=['NCEP_OBS_HEAT_TRANSPORT_ALL_2'], x2func=(lambda x: x[0]),
            y2vars=['NCEP_OBS_HEAT_TRANSPORT_ALL_2' ],
            y2func=(lambda y: y[1][0]),
            plottype='2 line plot'  ),
        'CAM_NCEP_HEAT_TRANSPORT_ATLANTIC': plotspec(
            vid='CAM_NCEP_HEAT_TRANSPORT_ATLANTIC',
            x1vars=['FSNS_ANN_latlon_1'], x1func=latvar,
            y1vars=['CAM_HEAT_TRANSPORT_ALL_1' ],
            y1func=(lambda y: y[0]),
            x2vars=['NCEP_OBS_HEAT_TRANSPORT_ALL_2'], x2func=(lambda x: x[0]),
            y2vars=['NCEP_OBS_HEAT_TRANSPORT_ALL_2' ],
            y2func=(lambda y: y[1][1]),
            plottype='2 line plot'  ),
        'CAM_NCEP_HEAT_TRANSPORT_INDIAN': plotspec(
            vid='CAM_NCEP_HEAT_TRANSPORT_INDIAN',
            x1vars=['FSNS_ANN_latlon_1'], x1func=latvar,
            y1vars=['CAM_HEAT_TRANSPORT_ALL_1' ],
            y1func=(lambda y: y[0]),
            x2vars=['NCEP_OBS_HEAT_TRANSPORT_ALL_2'], x2func=(lambda x: x[0]),
            y2vars=['NCEP_OBS_HEAT_TRANSPORT_ALL_2' ],
            y2func=(lambda y: y[1][2]),
            plottype='2 line plot'  ),
        'CAM_NCEP_HEAT_TRANSPORT_ALL':
            ['CAM_NCEP_HEAT_TRANSPORT_GLOBAL','CAM_NCEP_HEAT_TRANSPORT_PACIFIC',
             'CAM_NCEP_HEAT_TRANSPORT_ATLANTIC','CAM_NCEP_HEAT_TRANSPORT_INDIAN'],
        'past_CAM_HEAT_TRANSPORT_GLOBAL_1': plotspec(
            vid='CAM_HEAT_TRANSPORT_GLOBAL_1',
            xvars=['FSNS_ANN_latlon_1'], xfunc=latvar,
            yvars=['FSNS_ANN_latlon_1', 'FLNS_ANN_latlon_1', 'FLUT_ANN_latlon_1',
                    'FSNTOA_ANN_latlon_1', 'FLNT_ANN_latlon_1', 'FSNT_ANN_latlon_1',
                    'SHFLX_ANN_latlon_1', 'LHFLX_ANN_latlon_1', 'OCNFRAC_ANN_latlon_1' ],
            yfunc=oceanic_heat_transport, plottype='line plot'),
        'PRECT_JJA': ['PRECT_JJA_2line','PRECT_JJA_diff'],
        'PRECT_JJA_2line': plotspec(
            vid='PRECT_JJA_2line',
            x1vars=['PRECT_JJA_lat_1'], x1func = latvar,
            x2vars=['PRECT_JJA_lat_2'], x2func = latvar,
            y1vars=['PRECT_JJA_lat_1'], y1func=(lambda y: y),
            y2vars=['PRECT_JJA_lat_2'], y2func=(lambda y: y),
            plottype='2-line plot'),
        'PRECT_JJA_diff': plotspec(
            vid='PRECT_JJA_difference',
            xvars=['PRECT_JJA_lat_1','PRECT_JJA_lat_2'], xfunc = latvar_min,
            yvars=['PRECT_JJA_lat_1','PRECT_JJA_lat_2'],
            yfunc=aminusb_1ax,   # aminusb_1ax(y1,y2)=y1-y2; each y has 1 axis, use min axis
            plottype='line plot'),
        'TREFHT_ANN': plotspec(
            vid='TREFHT_ANN',xvars=['TREFHT_ANN_lat_1'], xfunc = latvar,
            yvars=['TREFHT_ANN_lat_1'], yfunc=(lambda y: y), plottype='line plot'),
        'TREFHT_DJF': ['TREFHT_DJF_2line','TREFHT_DJF_diff'],
        'TREFHT_DJF_2line': plotspec(
            vid='TREFHT_DJF_2line',
            x1vars=['TREFHT_DJF_lat_1'], x1func = latvar,
            x2vars=['TREFHT_DJF_lat_2'], x2func = latvar,
            y1vars=['TREFHT_DJF_lat_1'], y1func=(lambda y: y),
            y2vars=['TREFHT_DJF_lat_2'], y2func=(lambda y: y),
            plottype='2-line plot'),
        'TREFHT_DJF_diff': plotspec(
            vid='TREFHT_DJF_diff',
            xvars=['TREFHT_DJF_lat_1','TREFHT_DJF_lat_2'], xfunc = latvar_min,
            yvars=['TREFHT_DJF_lat_1','TREFHT_DJF_lat_2'],
            yfunc=aminusb_1ax,   # aminusb_1ax(y1,y2)=y1-y2; each y has 1 axis, use min axis
            plottype='line plot'),
        'TREFHT_DJF_line': plotspec(
            vid='TREFHT_DJF_line',
            xvars=['TREFHT_DJF_lat_1'], xfunc = latvar,
            yvars=['TREFHT_DJF_lat_1'], plottype='line plot'),
        'TREFHT_DJF_contour': plotspec(
            vid='TREFHT_DJF_contour',
            xvars=['TREFHT_DJF_latlon_1'], xfunc = (lambda x: x),
            plottype='line plot'),
        #plotspec( vid='TREFHT_JJA',xvars=['TREFHT_JJA'], xfiletable=filetable1, xfunc = latvar,
        #          yvars=['TREFHT_JJA'], yfunc=(lambda y: y), plottype='line plot'),
        #plotspec(
        #    vid='ts_by_lat_old',   # suitable for filenames
        #    xfiletable=filetable1,
        #    xfunc = latvar, # function to return x axis values
        #    xvars = ['ts_lat_old'],    # names of variables or axes, args of xfunc
        #    yfiletable=filetable1, # can differ from xfiletable, e.g. comparing 2 runs
        #    yfunc = (lambda y: y), # function to return y axis values
        #    yvars = ['ts_lat_old'], # names of variables or axes, args of xfunc
        #    zfiletable=filetable1,
        #    zfunc = (lambda: None),
        #    zvars = [],         # would be needed for countour or 3D plot
        #    # ... the ?vars variable will be converted (using the filetable and
        #    # plotvars) to actual variables which become the arguments for a call
        #    # of ?func, which returns the data we write out for plotting use.
        #    plottype='line plot' ),
        'ts_by_lat': plotspec(
            vid='ts_by_lat',   # suitable for filenames
            xfunc = latvar, # function to return x axis values
            xvars = ['ts_lat_new'],    # names of variables or axes, args of xfunc
            yfunc = (lambda y: y), # function to return y axis values
            yvars = ['ts_lat_new'], # names of variables or axes, args of xfunc
            zfunc = (lambda: None),
            zvars = [],         # would be needed for countour or 3D plot
            # ... the ?vars variable will be converted (using the filetable and
            # plotvars) to actual variables which become the arguments for a call
            # of ?func, which returns the data we write out for plotting use.
            plottype='line plot' ),
        #plotspec( vid="ts_global_old",xvars=['ts_scalar_tropical_o'], xfiletable=filetable1 ),
        'ts_global': plotspec( vid="ts_global",xvars=['ts_scalar_tropical_n'] ),
        }

    # Plotspeckeys specifies what plot data we will compute and write out.
    # In the future we may add a command line option, or provide other ways to
    # define plotspeckeys.
    #plotspeckeys = [['TREFHT_DJF_2line','TREFHT_DJF_difference']]
    #plotspeckeys = ['TREFHT_DJF_2line']
    #plotspeckeys = ['NCEP_OBS_HEAT_TRANSPORT_GLOBAL_2','CAM_HEAT_TRANSPORT_ALL_1']
    #plotspeckeys = ['CAM_NCEP_HEAT_TRANSPORT_GLOBAL']
    #plotspeckeys = ['CAM_NCEP_HEAT_TRANSPORT_ALL']
    #plotspeckeys = ['T_ANN_VERT_CAM_OBS_ALL']
    #plotspeckeys = ['TREFHT_DJF_laton_ALL']
    #plotspeckeys = ['TREFHT_ANN_Npole_ALL']
    plotspeckeys = ['TREFHT_DJF']
    #plotspeckeys = ['GLOBAL_AVERAGES']

    # Find the variable names required by the plotspecs.
    varkeys = []
    for psk in plotspeckeys:
        if type(psk) is str and type(plotspecs[psk]) is list:
            psk = plotspecs[psk]
        if type(psk) is str:
            write_xml = False
            psl = [ plotspecs[psk] ]
        else:
            write_xml = True
            psl = [ plotspecs[k] for k in psk ]
            xml_name = '_'.join( [ ps._id for ps in psl ] ) +'.xml'
            h = open( xml_name, 'w' )
            h.write("<plotdata>\n")
        for ps in psl:
            varkeys = varkeys+ps.xvars+ps.x1vars+ps.x2vars+ps.x3vars
            varkeys = varkeys+ps.yvars+ps.y1vars+ps.y2vars+ps.y3vars
            varkeys = varkeys + ps.zvars + ps.zrangevars
    for key in varkeys:
        if key in derived_variables.keys():
            varkeys = varkeys + derived_variables[key]._inputs
    varkeys = list( set(varkeys) )

    # Compute the value of every variable we need.
    varvals = {}
    # First compute all the reduced variables
    for key in varkeys:
        if key in reduced_variables.keys():
            varvals[key] = reduced_variables[key].reduce()
    # Then use the reduced variables to compute the derived variables
    #   Note that the derive() method is allowed to return a tuple.  This way
    #   we can use one function to compute what's really several variables.
    for key in varkeys:
        if key in derived_variables.keys():
            varvals[key] = derived_variables[key].derive(varvals)

    # Now use the reduced and derived variables to compute the plot data.
    for psk in plotspeckeys:
        if type(psk) is str and type(plotspecs[psk]) is list:
            psk = plotspecs[psk]
        if type(psk) is str:
            write_xml = False
            psl = [ plotspecs[psk] ]
        else:
            write_xml = True
            psl = [ plotspecs[k] for k in psk ]
            xml_name = '_'.join( [ ps._id for ps in psl ] ) +'.xml'
            h = open( xml_name, 'w' )
            h.write("<plotdata>\n")
        varkeys = []
        for ps in psl:
            print "jfp preparing data for",ps._id
            xrv = [ varvals[k] for k in ps.xvars ]
            x1rv = [ varvals[k] for k in ps.x1vars ]
            x2rv = [ varvals[k] for k in ps.x2vars ]
            x3rv = [ varvals[k] for k in ps.x3vars ]
            yrv = [ varvals[k] for k in ps.yvars ]
            y1rv = [ varvals[k] for k in ps.y1vars ]
            y2rv = [ varvals[k] for k in ps.y2vars ]
            y3rv = [ varvals[k] for k in ps.y3vars ]
            yarv = [ varvals[k] for k in ps.yavars ]
            ya1rv = [ varvals[k] for k in ps.ya1vars ]
            zrv = [ varvals[k] for k in ps.zvars ]
            zrrv = [ varvals[k] for k in ps.zrangevars ]
            xax = apply( ps.xfunc, xrv )
            x1ax = apply( ps.x1func, x1rv )
            x2ax = apply( ps.x2func, x2rv )
            x3ax = apply( ps.x3func, x3rv )
            yax = apply( ps.yfunc, yrv )
            y1ax = apply( ps.y1func, y1rv )
            y2ax = apply( ps.y2func, y2rv )
            y3ax = apply( ps.y3func, y3rv )
            yaax = apply( ps.yafunc, yarv )
            ya1ax = apply( ps.ya1func, ya1rv )
            zax = apply( ps.zfunc, zrv )
            zr = apply( ps.zrangefunc, zrrv )
            if      (xax is None or len(xrv)==0) and (x1ax is None or len(x1rv)==0)\
                and (x2ax is None or len(x2rv)==0) and (x3ax is None or len(x3rv)==0)\
                and (yax is None or len(yrv)==0) and (y1ax is None or len(y1rv)==0)\
                and (y2ax is None or len(y2rv)==0) and (y3ax is None or len(y3rv)==0)\
                and (zax is None or len(zrv)==0):
                continue
            filename = ps._id+"_test.nc"
            g = cdms2.open( filename, 'w' )    # later, choose a better name and a path!
            # Much more belongs in g, e.g. axis and graph names.
            if xax is not None and len(xrv)>0:
                xax.id = 'X'
                g.write(xax)
            if x1ax is not None and len(x1rv)>0:
                x1ax.id = 'X1'
                g.write(x1ax)
            if x2ax is not None and len(x2rv)>0:
                x2ax.id = 'X2'
                g.write(x2ax)
            if x3ax is not None and len(x3rv)>0:
                x3ax.id = 'X3'
                g.write(x3ax)
            if yax is not None and len(yrv)>0:
                yax.id = 'Y'
                g.write(yax)
            if y1ax is not None and len(y1rv)>0:
                y1ax.id = 'Y1'
                g.write(y1ax)
            if y2ax is not None and len(y2rv)>0:
                y2ax.id = 'Y2'
                g.write(y2ax)
            if y3ax is not None and len(y3rv)>0:
                y3ax.id = 'Y3'
                g.write(y3ax)
            if yaax is not None and len(yarv)>0:
                yaax.id = 'YA'
                g.write(yaax)
            if ya1ax is not None and len(ya1rv)>0:
                ya1ax.id = 'YA1'
                g.write(ya1ax)
            if zax is not None and len(zrv)>0:
                zax.id = 'Z'
                g.write(zax)
            if zr is not None:
                zr.id = 'Zrange'
                g.write(zr)
            g.presentation = ps.plottype
            # Note: For table output, it would be convenient to use a string-valued variable X
            # to specify string parts of the table.  Butcdms2 doesn't support them usefully.
            # Instead we'll manage with a convention that a table row plotspec's id is the name of
            # the row, thus available to be printed in, e.g., the first column.
            if ps.plottype=="table row":
                g.rowid = ps._id
            g.close()
            if write_xml:
                h.write( "<ncfile>"+filename+"</ncfile>\n" )

        if write_xml:
            h.write( "</plotdata>\n" )
            h.close()


if __name__ == '__main__':
   if len( sys.argv ) > 1:
      from findfiles import *
      path1 = sys.argv[1]
      if len( sys.argv ) > 2:
          path2 = sys.argv[2]
      else:
          path2 = None
      if len(sys.argv)>3 and sys.argv[3].find('filt=')==0:  # need to use getopt to parse args
          filt2 = sys.argv[3]
          test_driver(path1,path2,filt2)
      else:
          test_driver(path1,path2)
   else:
      print "usage: plot_data.py root"
