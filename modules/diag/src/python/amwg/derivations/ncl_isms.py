#!/usr/local/uvcdat/bin/python

# Support functions like some found in NCL for CAM.

import numpy, cdms2
from numpy import pi, sin
def latAxis( mv ):
    "returns the latitude axis, if any, of a variable mv"
    lat_axis = None
    for ax in mv.getAxisList():
        if ax.id=='lat': lat_axis = ax
    return lat_axis

# ~/amwg/ncl/lib/ncarg/nclscripts/csm/contributed.ncl
def latRegWgt( lat ):
    """ usage: wgt = latRegWgt(lat)
    original ncl version by D. Shea
    """
    nlat = lat.shape[0]
    rad  = pi/180.0
    err  = 1e20
    eps  = 0.01                        # arbitrary (was 0.001)

    dlat = abs(lat[2]-lat[1])           # error check
    dlat_lo = dlat-eps
    dlat_hi = dlat+eps
    # For converting subscript ranges (slicing), note that NCL ranges are
    # inclusive but Python ranges don't include the top subscript...
    difflo = numpy.all( (lat[1:nlat]-lat[0:nlat-1])>=dlat_lo )
    diffhi = numpy.all( (lat[1:nlat]-lat[0:nlat-1])<=dlat_hi )
    diff = difflo and diffhi
    if not diff:
        print "latRegWgt: Expecting equally spaced latitudes"
        return err*numpy.ones(nlat)

    dlat = abs((lat[2]-lat[1])*rad)*0.5

    w    = cdms2.createVariable( numpy.zeros(nlat), axes=[lat] )
    # In converting from ncl, note that ncl do-loop ranges are inclusive...
    for nl in range(nlat):
        w[nl] = abs( sin(lat[nl]*rad+dlat) - sin(lat[nl]*rad-dlat))
                                        # poles
    if abs(lat[0]) > 89.9999:
        nl = 0
        w[nl] = abs( 1 - sin(pi/2 - dlat) )
    if abs(lat[nlat-1]) > 89.9999:
        nl = nlat-1
        w[nl] = abs ( 1 - sin(pi/2 - dlat))
    dNam = getattr( lat, 'id', None )
#  if (.not.ismissing(dNam)) then
#      w!0 = dNam
#      if (iscoord(lat, dNam)) then
#          w&$dNam$ = lat
#      end if
#  end if
    w.long_name = "latitude weight"
    return( w )

# ~/amwg/amg_diag5.6/code/functions_surfaces.ncl
def get_ORO_OCNFRAC( infile, outfile ):
    if "ORO_OCNFRAC" in outfile.variables.keys():
        oro_ocnfrac = outfile['ORO_OCNFRAC']
    else:
        tmp = infile('OCNFRAC')[0,:,:]
        oro = abs(tmp-1.)           # ocnfrac = 1 becomes 0
        oro_ocnfrac = oro
        oro_ocnfrac.units = "dimensionless"
        oro_ocnfrac.long_name = "orography from ocnfrac"
        outfile['ORO_OCNFRAC'] = oro_ocnfrac
    return oro_ocnfrac

# ~/amwg/amg_diag5.6/code/functions_surfaces.ncl
def get_FSNS( infile, outfile ):
    if "FSNS" in outfile.variables.keys():
        fsns = outfile['FSNS']
    else:
        fsns = infile('FSNS')[0,:,:]
        fsns.long_name = "Surface net SW flux"
        fsns.units = "W/m~S~2~N~"
        outfile['FSNS'] = fsns
    return fsns

# ~/amwg/amg_diag5.6/code/functions_surfaces.ncl
def get_FLNS( infile, outfile ):
    if 'FLNS' in outfile.variables.keys():
        flns = outfile['FLNS']
    else:
        flns = infile('FLNS')[0,:,:]
        flns.long_name = "Surface net LW flux"
        flns.units = "W/m~S~2~N~"
        outfile['FLNS'] = flns
    return flns

# ~/amwg/amg_diag5.6/code/functions_surfaces.ncl
def get_SHFLX( infile, outfile ):
    if 'SHFLX' in outfile.variables.keys():
        shflx = outfile['SHFLX']
    else:
        shflx = infile('SHFLX')[0,:,:]
        shflx.units = "W/m~S~2~N~"
        shflx.long_name = "Surf sensible heat"
        outfile['SHFLX'] = shflx
    return shflx

# ~/amwg/amg_diag5.6/code/functions_surfaces.ncl
def get_LHFLX(infile, outfile ):
    if 'LHFLX' in outfile.variables.keys():
        lhflx = outfile['LHFLX']
    else:
        qflx = infile('QFLX')[0,:,:]   # kg/(m^2 s)
        Lv = 2.501e6                   # J/kg
        if 'PRECSC' in infile.variables.keys() and 'PRECSL' in infile.variables.keys():
            Lf = 3.337e5                     # J/kg
            precc = infile('PRECC')[0,:,:]   # m/s
            precl = infile('PRECL')[0,:,:]   # m/s
            precsc = infile('PRECSC')[0,:,:] # m/s
            precsl = infile('PRECSL')[0,:,:] # m/s
            tmp = qflx
            tmp = (Lv+Lf)*qflx - Lf*1.e3*(precc+precl-precsc-precsl)
            tmp.derive_op = "(Lv+Lf)*qflx-Lf*(prect-precsc-precl)"
        else:
            tmp = Lv*qflx              # W/m^2
            tmp.derive_op = "Lv*qflx"
        tmp.units = "W/m~S~2~N~"
        tmp.long_name = "Surf latent heat flux"
        lhflx = tmp
        outfile['LHFLX'] = lhflx
    return lhflx

# ~/amwg/amg_diag5.6/code/functions_transport.ncl
# calculate the ocean heat transport for models
def oht_model( gw, oro, fsns, flns, shfl, lhfl ):
    """parameters; must be dimensioned as specified:
    gwi  : gaussian weights (lat)
    oroi : orography data array (lat,lon)
      requires the lat and lon are attached coordinates of oro 
      and that oro and the following variables are 2D arrays (lat,lon).
    fsnsi: net shortwave solar flux at surface (lat,lon)
    flnsi: net longwave solar flux at surface (lat,lon)
    shfli: sensible heat flux at surface  (lat,lon)
    lhfli: latent heat flux at surface  (lat,lon)
    """
    re = 6.371e6            # radius of earth
    coef = re**2/1.e15      # scaled by PW
    heat_storage = 0.3      # W/m^2 adjustment for ocean heat storage 

    nlat = oro.shape[0]
    nlon = oro.shape[1]
    dlon = 2.*pi/nlon       # dlon in radians
    lat = latAxis(oro)
    i65n = numpy.where( lat[:]>=65 )[0][0]   # assumes that lat[i+1]>lat[i]
    i65s = numpy.where( lat[:]<=-65 )[0][-1]  # assumes that lat[i+1]>lat[i]

    # get the mask for the ocean basins
    basins_mask = ocean_mask(oro)    # returns 2D array(lat,lon) 
    # compute net surface energy flux
    netflux = fsns-flns-shfl-lhfl-heat_storage

    # compute the net flux for the basins
    netflux_basin = numpy.ma.empty( (3,nlat,nlon) )
    netflux_basin[0,:,:] = netflux[:,:]
    netflux_basin[1,:,:] = netflux[:,:]
    netflux_basin[2,:,:] = netflux[:,:]
    netflux_basin._mask[0,:,:] = numpy.not_equal(basins_mask,1) # False on Pacific
    netflux_basin._mask[1,:,:] = numpy.not_equal(basins_mask,2) # False on Atlantic
    netflux_basin._mask[2,:,:] = numpy.not_equal(basins_mask,3) # False on Indian

    # sum flux over the longitudes in each basin
    heatflux = numpy.ma.sum( netflux_basin, axis=2 )

    # compute implied heat transport in each basin
    oft = cdms2.createVariable( numpy.ma.masked_all((4,nlat)) )
    oft.setAxisList( [cdms2.createAxis([0,1,2,3],id='basin numer'),lat] )
    # These ! signs assign a name to a dimension of oft:
    #oft!0 = "basin number"   # 0:pacific, 1:atlantic, 2:indian, 3:total
    #oft!1 = "lat"

    for n in range(3):
        for j in range(i65n,i65s-1,-1):      #start sum at most northern point
            # ...assumes that lat[i+1]>lat[i]
            oft[n,j] = -coef*dlon*numpy.ma.sum( heatflux[n,j:i65n+1]*gw[j:i65n+1] )

    # compute total implied ocean heat transport at each latitude
    # as the sum over the basins at that latitude
    for j in range( i65n, i65s-1, -1 ):
        oft[3,j] = numpy.ma.sum( oft[0:3,j] )

    return oft       # 2D array(4,lat)


# ~/amwg/amg_diag5.6/code/functions_transport.ncl
def ocean_mask( oro ):
    """
    creates mask file for the pacific, atlantic and indian ocean basins
    oro: orography data array; must be dimensioned (lat,lon)
    and have the corresponding axes;
    and oro has values ocean: 0, land: 1, seaice: 2
    """
#jfp: It would be much better to read in the CMIP5 fx variable 'basin' if available.
#jfp: That is basically the same idea as the basin_mask computed here,
#jfp: though I don't know whether the values 0-4 have the same meaning.

    lat = oro.getAxisList()[0]
    lon = oro.getAxisList()[1]
    nlat = lat.shape[0]
    nlon = lon.shape[0]

    # make 2D mask array for ocean grid points
    #was:
    #basins_mask = cdms2.createVariable( oro, copy=True, id='basins_mask' )
    #if not hasattr(basins_mask,'_fill_value'):
    #    basins_mask._fill_value = 1.0e20
    #basins_mask[:] = basins_mask._fill_value
    #basins_mask.long_name = "(1)pacific (2)atlantic (3)indian"
    basins_mask = numpy.zeros( oro.shape )

    oroarr = numpy.array( oro[:] )
    wh = numpy.where( oroarr<0.5 )
    lln = numpy.array( lon[:] )
    llt = numpy.array( lat[:] )

    # Pacific ocean basin
    for k in range(len(wh[0])):
        j = wh[0][k]
        i = wh[1][k]
        if ( ( lln[i]>100.0 and lln[i]<260.0 and
               llt[j]< 65.0 and llt[j]> 15.0 )
             or
             ( lln[i]>100.0 and lln[i]<275.0 and
               llt[j]<= 15.0 and llt[j]> 10.0 )
             or
             ( lln[i]>100.0 and lln[i]<290.0 and
               llt[j]<= 10.0 and llt[j]> -5.0 )
             or
             ( lln[i]>=130.0 and lln[i]<=290.0 and
               llt[j]<= -5.0 )
             ): 
            basins_mask[j,i] = 1       # pacific

    # Atlantic ocean basin 
    for k in range(len(wh[0])):
        j = wh[0][k]
        i = wh[1][k]
        if ( ( lln[i]>290.0 and lln[i]<360.0 and
               llt[j]<= 65.0 and llt[j]> 45.0 )
             or
             ( lln[i]>=  0.0 and lln[i]< 10.0 and
               llt[j]<= 65.0 and llt[j]> 45.0 )
             or
             ( lln[i]>260.0 and lln[i]<360.0 and
               llt[j]<= 45.0 and llt[j]> 40.0 )
             or
             ( lln[i]>260.0 and lln[i]<355.0 and
               llt[j]<= 40.0 and llt[j]> 15.0 )
             or
             ( lln[i]>275.0 and lln[i]<360.0 and
               llt[j]<= 15.0 and llt[j]> 10.0 )
             or
             ( lln[i]>=  0.0 and lln[i]< 25.0 and
               llt[j]<= 15.0 and llt[j]> 10.0 )
             or
             ( lln[i]>290.0 and lln[i]<360.0 and
               llt[j]<= 10.0 )
             or
             ( lln[i]>=  0.0 and lln[i]< 25.0 and
               llt[j]<= 10.0 )
             ):
            basins_mask[j,i] = 2      # atlantic

    # Indian ocean basin
    for k in range(len(wh[0])):
        j = wh[0][k]
        i = wh[1][k]
        if (
            ( lln[i]>60.0 and lln[i]<100.0 and
              llt[j]< 25.0 and llt[j]> 20.0 )
            or
            ( lln[i]> 45.0 and lln[i]<100.0 and
              llt[j]<= 20.0 and llt[j]>  0.0 )
            or
            ( lln[i]>= 25.0 and lln[i]<100.0 and
              llt[j]<=  0.0 and llt[j]> -5.0 )
            or
            ( lln[i]>= 25.0 and lln[i]<=130.0 and
              llt[j]<= -5.0 )
            ):
            basins_mask[j,i] = 3     # indian

    return basins_mask     # returns 2D mask array (lat,lon)


