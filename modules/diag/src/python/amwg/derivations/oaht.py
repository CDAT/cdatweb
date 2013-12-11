#!/usr/local/uvcdat/bin/python

# Ocean and atmospheric heat transport
# Based on NCAR's plot_oaht.ncl
# pcmdi11.llnl.gov:~painter1/amwg/amwg_diag5.6/code/plot_oaht.ncl

import os
from ncl_isms import *

# NCAR gets thse from environment variables!  We have to do it better, but for now, do it worse!
version = None
compare = 'OBS'
wkdir      = None
plot_type  = None
color_type = None
time_stamp = None
case_names = None
ncdf_mode  = None
infilename1    = None
outfilename1   = None
infilename2    = None


# --------------------------------------------------------------------------
# MODEL 1 
def get_variables_for_atmospheric_heat_transport( infilename1, outfilename1, compare ):
    infile1 = cdms2.open(infilename1)
    outfile1 = cdms2.open(outfilename1,"w")
    case1 = infile1.case     # e.g. "b30.009"
    lat1 = infile1['lat']
    nlat1 = lat1.shape

    # Gauss weights:
    if 'gw' in f.variables.keys():
        gw = infile1['gw']
    elif 'wgt' in infile1.variables.keys():
        gw = infile1['wgt']
    else:   # no Gauss weights in file
        gw = cdms2.createVariable( latRegWgt(lat1), axes=[lat1] )

    oro = get_ORO_OCNFRAC(infile1,outfile1)
    fsns = get_FSNS(infile1,outfile1)
    flns = get_FLNS(infile1,outfile1)
    shflx = get_SHFLX(infile1,outfile1)
    lhflx = get_LHFLX(infile1,outfile1)

    if 'FLUT' in infile1.variables.keys():
        flut = get_FLUT( infile1, outfile1 ) # <<< this function doesn't exist 
        fsntoa = get_FSNTOA( infile1,outfile1 ) # <<< this function doesn't exist 
    else:
        flut = None
        flnt = get_FLNT(infile1,outfile1)
        fsnt = get_FSNT( infile1, outfile1 )   # <<< this function doesn't exist 

def oceanic_heat_transport(
    fsns, flns, flut, fsntoa, flnt, fsnt, shflx, lhflx, ocnfrac,
    gw=None, oro=None, compare="OBS" ):
    # All the required variables are available in typical CAM output.
    # Sometimes lhflx isn't available but it can be computed - c.f. get_LHFLX().
    # For the moment we'll require it.
    # gw is sometimes available; and ocnfrac or oro is normally available.
    # compare isn't used at the moment, but it's in a remnant of NCL code below.

    lat1 = latAxis(fsns)

    if gw==None:
        gw = cdms2.createVariable( latRegWgt(lat1), axes=[lat1] )
    if oro is None:
        if ocnfrac is None:
            print("ERROR, cannot compute atmospheric_heat_transport without oro or ocnfrac")
        oro = abs(ocnfrac-1.)           # ocnfrac = 1 becomes 0

    # get the model ocean heat transport for the basins and total 
    oht1 = oht_model( gw, oro, fsns, flns, shflx, lhflx )

    return oht1

    # The following computes aht1, which I'm not using yet...

# heat transport (ported from NCAR code; not used here)
    if compare != "OBS":
        print "ERROR in atmospheric_heat_transport() - compare=",compare,\
            " but non-obs not done yet!"
        #  ht1 = ht_surface(gw,oro,fsns,flns,shflx,lhflx,False) # <<< this function doesn't exist 
        #  ht1c = ht_surface(gw,oro,fsns,flns,shflx,lhflx,True) # <<< this function doesn't exist 

    # get the model required heat transport at TOA
    if not flut is None:
        restoa = fsntoa - flut
    else:                                        # ccm3.6
        restoa = fsnt - flnt
    rht1 = rht_model( gw, restoa )               # (nlat1)

    # Compute model atmospheric heat transport from rht and ocean
    aht1 = cdms2.createVariable( rht1 - oht1[3,:],     # (nlat1)
                                 axes=[lat1], id='atmosheattransp' )

    return aht1

# pcmdi11:~painter1/amwg/amwg_diag5.6/code/functions_transport.ncl
def rht_model( gw, restoa ):
    """ calculate the required heat transport from data at TOA 
    gw : gaussian weights dimensioned (lat)
    restoa : residual energy at TOA = fsntoa-flut  dimensioned (lat,lon)
    """

    # constants
    re = 6.371e6            # radius of earth
    coef = re**2/1.e15       # scaled for PW 

    nlat = restoa.shape[0]
    nlon = restoa.shape[1]
    dlon = 2.*pi/nlon       # dlon in radians
    lat = latAxis(restoa)

    # sum flux over the longitudes 
    heatflux = numpy.ma.sum( restoa, axis=1 )  

    # compute required heat transport
    rht = cdms2.createVariable( heatflux, copy=True )
    for j in range(nlat-1,-1,-1):      #start sum at most northern point 
        rht[j] = -coef*dlon*numpy.ma.sum( heatflux[j:nlat]*gw[j:nlat] )

    return(rht)     # 1D array(nlat)

# pcmdi11:~painter1/amwg/amwg_diag5.6/code/plot_oaht.ncl around line 200
def ncep_ocean_heat_transport( path ):
    """This is a very special-purpose function to read a particular file, named
       ANNUAL_TRANSPORTS_1985_1989.ascii .   Some columns provide ocean heat transport obs data
       which is useful for comparing with model output.
       The input argument is a path in which the file may be found.
       There are two return values (i.e., a 2-tuple).  The first is the latitude array, length 64.
       The second is a 4x64 array, containing heat transport values for each latitude.
       The first index is 0 for the Pacific Ocean basin, 1 for Atlantic, 2 for Indian, and 3 for
       all oceans.
       """
    # NCEP REANALYSIS AND ERBE DATA
    # read in NCEP meridional transport data by Trenberth and Caron 
    # which uses T42 latitudes
    if type(path) is str:
        # simple case, path is a string
        f = open( os.path.normpath( path+'/ANNUAL_TRANSPORTS_1985_1989.ascii' ) )
    elif hasattr(path,'_filelist'):
        # path isn't a path string, it's a filetable.
        # We'll get paths out of it and look for what we need there.
        paths = set([os.path.dirname(f) for f in path._filelist.files])
        for p in paths:
            filep = os.path.normpath( p+'/ANNUAL_TRANSPORTS_1985_1989.ascii' )
            if os.path.isfile(filep):
                f = open( filep )
                break
    else:
        raise Exception(
            "ncep_ocean_heat_transport() cannot find path needed for NCEP heat transport obs")
    nlatT42 = 64   # T42 latitudes
    i65s = 8       # index of T42 latitude 65S
    i65n = 55      # index of T42 latitude 65N
    lines = f.readlines()
    f.close()
    # ncep should have 64 lines each with 22 numbers.
    # We're dropping the 65th line, which is column footers.
    ncep = numpy.array([ [float(a) for a in l.split(' ') if a!=''] for l in lines[0:nlatT42] ])
    T42lat = ncep[:,0]/100.
#    erbe_rhst = ncep[:,1]/100.       # global surface RHT from ERBE TOA (not used yet)
    ncep_oht = numpy.ma.masked_all((4,nlatT42))
    for l in range(nlatT42):
        if ncep[l,8]>-999:
            ncep_oht[0,l] = ncep[l,8]/100.    # NCEP pacific ocean basin transport
        if ncep[l,7]>-999:
            ncep_oht[1,l] = ncep[l,7]/100.    # NCEP atlantic ocean basin transport
        if ncep[l,9]>-999:
            ncep_oht[2,l] = ncep[l,9]/100.    # NCEP indian ocean basin transport
        if ncep[l,4]>-999:
            ncep_oht[3,l] = ncep[l,4]/100.    # NCEP total ocean basin transport
    ncep_oht[1,i65n+1] = ncep_oht.get_fill_value()      # set to missing since > 65N
    ncep_oht.mask[1,i65n+1] = True
    ncep_oht[3,0:i65s] = ncep_oht.get_fill_value()     # set values outside of 65N to 65S
    ncep_oht.mask[3,0:i65s] = True
    ncep_oht[3,i65n+1:64] = ncep_oht.get_fill_value()  # to missing
    ncep_oht.mask[3,i65n+1:64] = True

    basin = cdms2.createAxis( [0,1,2,3], id='basin' )
    lat = cdms2.createAxis( T42lat, id='lat' )
    latv = cdms2.createVariable(lat,axes=[lat])
    oht = cdms2.createVariable(ncep_oht,axes=[basin,lat])
    return (latv,oht)
# not used yet...
## atmospheric heat transport from ERBE and NCEP (ocean) 
#ncep_aht = numpy.ma.masked_all(nlatT42)
#ncep_aht = erbe_rht-ncep_oht[3,:]
