from metrics.computation.reductions import *

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
