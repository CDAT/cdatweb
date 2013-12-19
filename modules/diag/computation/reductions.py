#!/usr/local/uvcdat/bin/python

# Data reduction functions.

import cdms2, math, itertools, operator, numpy, subprocess, re
import hashlib, os
import pprint
import cdutil.times
from math import radians
from numpy import sin, ma
import dateutil.parser
from datetime import datetime as datetime
from unidata import udunits
from cdutil import averager
from metrics.amwg.derivations import press2alt
from metrics.fileio.filetable import *
#from climo_test import cdutil_climatology

seasonsDJF=cdutil.times.Seasons(['DJF'])
seasonsJJA=cdutil.times.Seasons(['JJA'])
seasons2=cdutil.times.Seasons(['DJF','JJA'])
seasons4=cdutil.times.Seasons(['DJF','MAM','JJA','SON'])
seasonsyr=cdutil.times.Seasons('JFMAMJJASOND')
seasonsmons=cdutil.times.Seasons(
    ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC'])


# >>>> TO DO: accomodate more names for the level axis.  Much of this can be
# >>>> done simply by adding more names in levAxis().  Search on 'lev' for the rest.
# >>>> in this file.  E.g. LMWG uses levlk and levgrnd.

def allAxes( mv ):
    """returns a list of axes of a variable mv"""
    if mv is None: return None
    return mv.getAxisList()

def latAxis( mv ):
    "returns the latitude axis, if any, of a variable mv"
    if mv is None: return None
    lat_axis = None
    for ax in allAxes(mv):
        if ax.id=='lat': lat_axis = ax
    return lat_axis

def latAxis2( mv ):
    "returns the latitude axis, if any, of a variable mv; and the index in its axis list"
    if mv is None: return None
    lat_axis = None
    idx = None
    for i,ax in enumerate(allAxes(mv)):
        if ax.id=='lat':
            lat_axis = ax
            idx = i
    return lat_axis,idx

def lonAxis( mv ):
    "returns the longitude axis, if any, of a variable mv"
    if mv is None: return None
    lon_axis = None
    for ax in allAxes(mv):
        if ax.id=='lon': lon_axis = ax
    return lon_axis

def levAxis( mv ):
    "returns the level axis, if any, of a variable mv"
    if mv is None: return None
    lev_axis = None
    for ax in allAxes(mv):
        if ax.id=='lev':
            lev_axis = ax
            break
        if ax.id=='plev':
            lev_axis = ax
            break
    return lev_axis

def timeAxis( mv ):
    "returns the time axis, if any, of a variable mv"
    if mv is None: return None
    time_axis = None
    for ax in allAxes(mv):
        if ax.id=='time': time_axis = ax
    return time_axis

def tllAxes( mv ):
    "returns the time,latitude, and longitude axes, if any, of a variable mv"
    if mv is None: return None
    for ax in allAxes(mv):
        if ax.id=='lat': lat_axis = ax
        if ax.id=='lon': lon_axis = ax
        if ax.id=='time': time_axis = ax
    return (time_axis,lat_axis,lon_axis)

def fix_time_units( timeunits ):
    """Sometimes we get time units which aren't compatible with cdtime.
    This function will (try to) fix them.  The input argument is a string, e.g.
    "months since Jan 1979" and the return value is another string, e.g.
    "months since 1979-01-09 00:00:00".  If no better string can be found,
    then the input timeunits will be returned.
    """
    imon = timeunits.find("months since ")
    if imon==0:
        since="months since "
    else:
        iday = timeunits.find("days since ")
        if iday==0:
            since="days since "
        else:
            ihour = timeunits.find("hours since ")
            if ihour==0:
                since="hours since "
            else:
                return timeunits
    date = timeunits[len(since):]
    date_is_bc = False
    if date.find('B.C.')>0:  # I've seen one example like this!
        # B.C. fixup isn't tested!
        date_is_bc = True
        # e.g. "January 1, 4713 B.C."  Note exactly one space before B. And not BC etc.
        matchobject = re.search( r"\d+\sB\.C\." )   # not tested
        if matchobject is None:
            return timeunits
        pre_yr = matchobject.start()
        pre_bc = matchobject.end() - 5  #2 spaces before B.C. would need -6 or another re
        yr_bc = date[pre_yr:pre_bc]
        yr_ad = str(1 - int(yr))
        # The parser won't understand negative years, but cdtime will.  So don't
        # fix the date quite yet...
        date = date[0:pre_bc]
    new_date = str( dateutil.parser.parse( date, default=datetime(1850,1,1,0,0)) )
    if date_is_bc:
        pre_yr = new_date.find(yr_bc)
        new_date = new_date[0:pre_yr]+yr_ad+new_date[pre_yr+len(yr_bc)]
    return since+new_date

def restrict_lat( mv, latmin, latmax ):
    """Input is a variable which depends on latitude.
    This function will copy it to a new variable, except that the new variable's
    latitude axis will be restricted to latmin<=lat<=latmax; and of course the
    data will be restricted to correspond."""
    if latmin==-90: latmin = -91  # just to make sure
    if latmax==90:  latmax = 91

    # axes
    latax,idx = latAxis2(mv)
    if latax is None: return None
    imin = min( [i for i in range(len(latax)) if latax[i]>=latmin and latax[i]<=latmax ] )
    imax = max( [i for i in range(len(latax)) if latax[i]>=latmin and latax[i]<=latmax ] )
    newlatax = latax.subaxis( imin, imax+1 )
    # TO DO: use latax.bounds (if present) for newlatax.bounds
    # At the moment, I'm working with data for which latax.bounds doesn't exist.
    # At the moment, we don't need bounds.  This would get us through if necessary:
    # newlatax.bounds = newlatax.genGenericBounds()
    newaxes = list( allAxes(mv) ) # shallow copy
    newaxes[idx] = newlatax

    # shrink the data to match the shrunk lat axis
    newmv_shape = list( mv.shape )
    newmv_shape[idx] = imax+1 - imin
    if imin>0:
        nd = numpy.delete( mv.data, slice(0,imin), idx ) # doesn't change mv
    else:
        nd = mv
    lenidx  = nd.shape[idx]
    if lenidx > newmv_shape[idx]:
        newdata = numpy.delete( nd.data, slice(imax+1-imin,lenidx), idx )
    else:
        newdata = nd

    # new variable
    newmv = cdms2.createVariable( newdata, copy=True, axes=newaxes, id=mv.id )
    newmv.units = mv.units
    return newmv

def reduce2scalar_zonal_old( mv, latmin=-90, latmax=90, vid=None ):
    """returns the mean of the variable over the supplied latitude range (in degrees, based
    on values of lat, not lat_bnds)
    The computed quantity is a scalar but is returned as a cdms2 variable, i.e. a MV.
    The input mv is a cdms2 variable, assumed to be indexed as is usual for CF-compliant variables,
    i.e. mv(time,lat,lon).  At present, no other axes (e.g. level) are supported.
    At present mv must depend on all three axes.
    ....This function is deprecated - use the version which uses the avarager() function....
    """
    # For now, I'm assuming that the only axes are time,lat,lon - so that zm is a scalar.
    # And I'm assuming equal spacing in lon (so all longitudes contribute equally to the average)
    # If they aren't, it's best to use area from cell_measures attribute if available; otherwise
    # compute it with lat_bnds, lon_bnds etc.
    if vid==None:
        vid = 'reduced_'+mv.id
    time,lat,lon = tllAxes(mv)
    if hasattr(mv.parent,'variables'):
        fil = mv.parent # mv is a fileVariable and fil is a file.
        lat_bnds = fil[lat.bounds]
    else:
        lataxis = latAxis(mv)   # mv is a TransientVariable
        lat_bnds = lataxis._bounds_

    mvta = timeave_old( mv )

    # In computing the average, we use area weighting.
    # Sometimes the area is available in cell_measures, but for now I'll just use the backup method:
    # The area of a lonlat cell is   R^2*delta(lon)*delta(sin(lat)).
    # With equally spaced lon, we don't need delta(lon) for weights.
    # I'll assume that lat,lon are in degrees, which is the only way I've ever seen them.
    wgtsum = 0
    zm = 0
    for i,lati in enumerate(lat):
        # The following test could be sped up a lot, because lat[i] is ordered...
        # >>> to do: partial overlaps
        if latmin<=lati and lati<latmax:
            latlo = lat_bnds[i,0]
            lathi = lat_bnds[i,1]
            wgti = sin(radians(lathi))-sin(radians(latlo))
            zi = 0.0
            for j in range(len(lon)):
                zi += mvta[i,j]
            zi *= wgti
            wgtsum += wgti*len(lon)
            zm += zi
    zm /= wgtsum
    # zm is a scalar, so createVariable gets no axes argument:
    zmv = cdms2.createVariable( zm, id=vid )
    return zmv

def reduce2scalar_zonal( mv, latmin=-90, latmax=90, vid=None ):
    """returns the mean of the variable over the supplied latitude range (in degrees, based
    on values of lat, not lat_bnds)
    The computed quantity is a scalar but is returned as a cdms2 variable, i.e. a MV.
    The input mv is a cdms2 variable too.
    This function uses the cdms2 avarager() function to handle weights and do averages
    """
    if vid==None:
        vid = 'reduced_'+mv.id
    axes = allAxes( mv )
    ilat = None
    for i,ax in enumerate(axes):
        if ax.id=='lat': ilat = i
    # reduce size of lat axis to (latmin,latmax)
    # Let's home a direct search will be fast enough:
    lataxis = latAxis( mv )
    lmin = -1
    lmax = len(lataxis)
    if lataxis[0]>=latmin: lmin = 0
    if lataxis[-1]<=latmax: lmax = len(lataxis)-1
    if lmin==-1 or lmax==len(lataxis):
        for l,ax in enumerate(lataxis):
            if lmin==-1 and ax>=latmin: lmin = max( 0, l )
            if lmax==len(lataxis) and ax>=latmax: lmax = min( l, len(lataxis) )
    lataxis_shrunk = lataxis.subaxis(lmin,lmax)
    mv2shape = list(mv.shape)
    mv2shape[ilat] = lmax-lmin+1
    axes[ilat] = lataxis_shrunk
    mvd1 = numpy.delete( mv, slice(0,lmin), ilat )
    mvdata = numpy.delete( mvd1, slice(lmax-lmin,len(lataxis)-lmin), ilat )
    mv2 = cdms2.createVariable( mvdata, axes=axes )

    axis_names = [ a.id for a in axes ]
    axes_string = '('+')('.join(axis_names)+')'
    avmv = averager( mv2, axis=axes_string )
    avmv.id = vid   # Note that the averager function returns a variable with meaningless id.
    ammv.units = mv.units

    return avmv

def reduce2scalar( mv, vid=None ):
    """averages mv over the full range all axes, to a single scalar.
    Uses the averager module for greater capabilities"""
    if vid==None:   # Note that the averager function returns a variable with meaningless id.
        vid = 'reduced_'+mv.id
    axes = allAxes( mv )
    axis_names = [ a.id for a in axes ]
    axes_string = '('+')('.join(axis_names)+')'

    avmv = averager( mv, axis=axes_string )
    avmv.id = vid
    avmv.units = mv.units

    return avmv

def reduce2lat_old( mv, vid=None ):
    """returns the mean of the variable over all axes but latitude, as a cdms2 variable, i.e. a MV.
    The input mv is a also cdms2 variable, assumed to be indexed as is usual for CF-compliant
    variables, i.e. mv(time,lat,lon).  At present, no other axes (e.g. level) are supported.
    At present mv must depend on all three axes.
    """
    # >>> For now, I'm assuming that the only axes are time,lat,lon
    # And I'm assuming equal spacing in lon (so all longitudes contribute equally to the average)
    # If they aren't, it's best to use area from cell_measures attribute if available; otherwise
    # compute it with lat_bnds, lon_bnds etc.
    # If I base another reduction function on this one, it's important to note that an average
    # in the lat direction will unavoidably need weights, because of the geometry.

    if vid==None:
        vid = 'reduced_'+mv.id
    time_axis, lat_axis, lon_axis = tllAxes( mv )

    mvta = timeave_old( mv )

    zm = numpy.zeros( mvta.shape[0] )
    for i in range(len(lat_axis)):
        for j in range(len(lon_axis)):
            zm[i] += mvta[i,j]
        zm[i] /= len(lon_axis)
    zmv = cdms2.createVariable( zm, axes=[lat_axis], id=vid )
    return zmv

def reduce2lat( mv, vid=None ):
    """as reduce2lat_old, but uses the averager module for greater capabilities"""
    if vid==None:   # Note that the averager function returns a variable with meaningless id.
        vid = 'reduced_'+mv.id
    axes = allAxes( mv )
    axis_names = [ a.id for a in axes if a.id!='lat' ]
    axes_string = '('+')('.join(axis_names)+')'

    avmv = averager( mv, axis=axes_string )
    avmv.id = vid
    avmv.units = mv.units

    return avmv

def reduce2levlat( mv, vid=None ):
    """as reduce2lat, but averaging reduces coordinates to (lev,lat)"""
    if vid==None:   # Note that the averager function returns a variable with meaningless id.
        vid = 'reduced_'+mv.id
    if levAxis(mv) is None: return None
    if latAxis(mv) is None: return None
    axes = allAxes( mv )
    timeax = timeAxis(mv)
    if timeax.getBounds()==None:
        timeax._bounds_ = timeax.genGenericBounds()
    axis_names = [ a.id for a in axes if a.id!='lev' and a.id!='lat' ]
    axes_string = '('+')('.join(axis_names)+')'

    avmv = averager( mv, axis=axes_string )
    avmv.id = vid
    avmv.units = mv.units

    return avmv

def reduce2levlat_seasonal( mv, seasons=seasonsyr, vid=None ):
    """as reduce2levlat, but data is averaged only for time restricted to the specified season;
    as in reduce2lat_seasona."""
    if vid==None:   # Note that the averager function returns a variable with meaningless id.
        vid = 'reduced_'+mv.id
    if levAxis(mv) is None: return None
    if latAxis(mv) is None: return None
    axes = allAxes( mv )
    timeax = timeAxis(mv)
    if timeax.getBounds()==None:
        timeax._bounds_ = timeax.genGenericBounds()

    if timeax.units=='months':
        # Special check necessary for LEGATES obs data, because
        # climatology() won't accept this incomplete specification
        timeax.units = 'months since 0001-01-01'
    mvseas = seasons.climatology(mv)

    axis_names = [ a.id for a in axes if a.id!='lev' and a.id!='lat' and a.id!='time']
    axes_string = '('+')('.join(axis_names)+')'

    if len(axes_string)>2:
        avmv = averager( mvseas, axis=axes_string )
    else:
        avmv = mvseas
    avmv.id = vid
    avmv = delete_singleton_axis( avmv, vid='time' )
    avmv.units = mv.units

    return avmv

def reduce2latlon( mv, vid=None ):
    """as reduce2lat, but averaging reduces coordinates to (lat,lon)"""
    if vid==None:   # Note that the averager function returns a variable with meaningless id.
        vid = 'reduced_'+mv.id
    axes = allAxes( mv )
    axis_names = [ a.id for a in axes if a.id!='lat' and a.id!='lon' ]
    axes_string = '('+')('.join(axis_names)+')'
    for ax in axes:
        # The averager insists on bounds.  Sometimes they don't exist, especially for obs.
        if ax.id!='lat' and ax.id!='lon' and not hasattr( ax, 'bounds' ):
            ax.setBounds( ax.genGenericBounds() )

    avmv = averager( mv, axis=axes_string )
    avmv.id = vid
    avmv.units = mv.units

    return avmv

def reduce_time( mv, vid=None ):
    """as reduce2lat, but averaging reduces only the time coordinate"""
    if vid==None:   # Note that the averager function returns a variable with meaningless id.
        vid = 'reduced_'+mv.id
    axes = allAxes( mv )
    axis_names = [ a.id for a in axes if a.id=='time' ]
    axes_string = '('+')('.join(axis_names)+')'
    if len(axes_string)>2:
        for ax in axes:
            # The averager insists on bounds.  Sometimes they don't exist, especially for obs.
            if ax.id!='lat' and ax.id!='lon' and not hasattr( ax, 'bounds' ):
                ax.setBounds( ax.genGenericBounds() )
        avmv = averager( mv, axis=axes_string )
    else:
        avmv = mv
    avmv.id = vid
    avmv.units = mv.units

    return avmv

def reduce2lat_seasonal( mv, seasons=seasonsyr, vid=None ):
    """as reduce2lat, but data is used only for time restricted to the specified season.  The season
    is specified as an object of type cdutil.ties.Seasons, and defaults to the whole year.
    The returned variable will still have a time axis, with one value per season specified.
    """
    if vid==None:
        vid = 'reduced_'+mv.id
    # Note that the averager function returns a variable with meaningless id.
    # The climatology function returns the same id as mv, which we also don't want.

    # The slicers in time.py require getBounds() to work.
    # If it doesn't, we'll have to give it one.
    # Setting the _bounds_ attribute will do it.
    for ax in mv.getAxisList():
        if ax.getBounds() is None:
            ax._bounds_ = ax.genGenericBounds()
    timeax = timeAxis(mv)
    if timeax.units=='months':
        # Special check necessary for LEGATES obs data, because
        # climatology() won't accept this incomplete specification
        timeax.units = 'months since 0001-01-01'
    mvseas = seasons.climatology(mv)
    if mvseas is None:
        # Among other cases, this can happen if mv has all missing values.
        return None
    
    axes = allAxes( mv )
    axis_names = [ a.id for a in axes if a.id!='lat' and a.id!='time']
    axes_string = '('+')('.join(axis_names)+')'

    if len(axes_string)>2:
        avmv = averager( mvseas, axis=axes_string )
    else:
        avmv = mvseas
    avmv.id = vid

    avmv = delete_singleton_axis( avmv, vid='time' )
    avmv.units = mv.units
    return avmv

def reduce2latlon_seasonal( mv, seasons=seasonsyr, vid=None ):
    """as reduce2lat_seasonal, but both lat and lon axes are retained.
    """
    # This differs from reduce2lat_seasonal only in the line "axis_names ="....
    # I need to think about how to structure the code so there's less cut-and-paste!
    if vid==None:
        vid = 'reduced_'+mv.id
    # Note that the averager function returns a variable with meaningless id.
    # The climatology function returns the same id as mv, which we also don't want.

    # The slicers in time.py require getBounds() to work.
    # If it doesn't, we'll have to give it one.
    # Setting the _bounds_ attribute will do it.
    timeax = timeAxis(mv)
    if timeax.getBounds()==None:
        timeax._bounds_ = timeax.genGenericBounds()
    mvseas = seasons.climatology(mv)
    
    axes = allAxes( mv )
    axis_names = [ a.id for a in axes if a.id!='lat' and a.id!='lon' and a.id!='time']
    axes_string = '('+')('.join(axis_names)+')'

    if len(axes_string)>2:
        for axis in mvseas.getAxisList():
            if axis.getBounds() is None:
                axis._bounds_ = axis.genGenericBounds()
        avmv = averager( mvseas, axis=axes_string )
    else:
        avmv = mvseas
    if avmv is None: return avmv
    avmv.id = vid
    if hasattr(mv,'units'): avmv.units = mv.units
    avmv = delete_singleton_axis( avmv, vid='time' )
    avmv.units = mv.units
    return avmv

def reduce_time_seasonal( mv, seasons=seasonsyr, vid=None ):
    """as reduce2lat_seasonal, but all non-time axes are retained.
    """
    if vid==None:
        vid = 'reduced_'+mv.id
    # Note that the averager function returns a variable with meaningless id.
    # The climatology function returns the same id as mv, which we also don't want.

    # The slicers in time.py require getBounds() to work.
    # If it doesn't, we'll have to give it one.
    # Setting the _bounds_ attribute will do it.
    timeax = timeAxis(mv)
    if timeax is None:
        print "WARNING- no time axis in",mv.id
        return None
    if timeax.getBounds()==None:
        timeax._bounds_ = timeax.genGenericBounds()
    mvseas = seasons.climatology(mv)
    if mvseas is None:
        print "WARNING- cannot compute climatology for",mv.id,seasons.seasons
        print "...probably there is no data for times in the requested season."
        return None
    avmv = mvseas
    avmv.id = vid
    if hasattr(mv,'units'): avmv.units = mv.units
    avmv = delete_singleton_axis( avmv, vid='time' )
    avmv.units = mv.units
    return avmv

def select_lev( mv, slev ):
    """Input is a level-dependent variable mv and a level slev to select.
    slev is an instance of udunits - thus it has a value and a units attribute.
    This function will create and return a new variable mvs without a level axis.
    The values of mvs correspond to the values of mv with level set to slev.
    Interpolation isn't done yet, but is planned !"""
    levax = levAxis(mv)
    # Get ig, the first index for which levax[ig]>slev
    # Assume that levax values are monotonic.
    dummy,slev = reconcile_units( levax, slev )  # new slev has same units as levax
    if levax[0]<=levax[-1]:
        ids = numpy.where( levax[:]>=slev.value )    # assumes levax values are monotonic increasing
    else:
        ids = numpy.where( levax[:]<=slev.value )    # assumes levax values are monotonic decreasing
    if ids is None or len(ids)==0:
        ig = len(levax)-1
    else:
        ig = ids[0][0]
    # Crude fist cut: don't interpolate, just return a value
    if levax == mv.getAxisList()[0]:
        mvs = cdms2.createVariable( mv[ig:ig+1,...], copy=1 )  # why ig:ig+1 rather than ig?  bug workaround.
    elif levax == mv.getAxisList()[1]:
        mvs = cdms2.createVariable( mv[:,ig:ig+1,...], copy=1 )
    else:
        print "ERROR, select_lev() does not support level axis except as first or second dimentions"
        return None
    return mvs

def latvar( mv ):
    """returns a transient variable which is dimensioned along the lat axis
    but whose values are the latitudes"""
    # First get the axis.  This is probably not as general as we'll need...
    if mv is None: return None
    lat_axis = latAxis(mv)
    #latmv = mv.clone()  # good if mv has only a lat axis
    #latmv[:] = lat_axis[:]
    latmv = cdms2.createVariable( lat_axis[:], axes=[lat_axis], id='lat',
                                  attributes={'units':lat_axis.units},
                                  copy=True )
    return latmv

def lonvar( mv ):
    """returns a transient variable which is dimensioned along the lon axis
    but whose values are the longitudes"""
    # First get the axis.  This is probably not as general as we'll need...
    if mv is None: return None
    lon_axis = lonAxis(mv)
    latmv = cdms2.createVariable( lon_axis[:], axes=[lon_axis], id='lon',
                                  attributes={'units':lon_axis.units},
                                  copy=True )
    return latmv

def levvar( mv ):
    """returns a transient variable which is dimensioned along the lev (level) axis
    but whose values are the levels"""
    # First get the axis.  This is probably not as general as we'll need...
    if mv is None: return None
    lev_axis = levAxis(mv)
    #levmv = mv.clone()  # good if mv has only a lev axis
    #levmv[:] = lev_axis[:]
    levmv = cdms2.createVariable( lev_axis[:], axes=[lev_axis], id='lev',
                                  attributes={'units':lev_axis.units},
                                  copy=True )
    return levmv

def pressures_in_mb( pressures ):
    """From a variable or axis of pressures, this function
    converts to millibars, and returns the result as a numpy array."""
    if not hasattr( pressures, 'units' ): return None
    if pressures.units=='mb':
        pressures.units = 'mbar' # udunits uses mb for something else
        return pressures[:]
    tmp = udunits(1.0,pressures.units)
    s,i = tmp.how('mbar')
    pressmb = s*pressures[:] + i
    return pressmb

def heightvar( mv ):
    """returns a transient variable which is dimensioned along the lev (level) axis
    and whose values are the heights corresponding to the pressure levels found
    as the lev axis of mv.  Levels will be converted to millibars.
    heights are returned in km"""
    if mv is None: return None
    lev_axis = levAxis(mv)
    heights = 0.001 * press2alt.press2alt( pressures_in_mb(lev_axis) )  # 1000 m = 1 km
    heightmv = cdms2.createVariable( heights, axes=[lev_axis], id=mv.id,
                                     attributes={'units':"km"} )
    return heightmv

def latvar_min( mv1, mv2 ):
    """returns a transient variable which is dimensioned as whichever of mv1, mv2
    has the fewest latitude points but whose values are the latitudes"""
    if mv1 is None: return None
    if mv2 is None: return None
    lat_axis1 = latAxis(mv1)
    lat_axis2 = latAxis(mv2)
    if len(lat_axis1)<=len(lat_axis2):
        lat_axis = lat_axis1
        mv = mv1
    else:
        lat_axis = lat_axis2
        mv = mv2
    latmv = cdms2.createVariable( lat_axis[:], axes=[lat_axis], id='lat',
                                  attributes={'units':lat_axis.units} )
    return latmv

def lonvar_min( mv1, mv2 ):
    """returns a transient variable which is dimensioned as whichever of mv1, mv2
    has the fewest longitude points but whose values are the longitudes"""
    if mv1 is None: return None
    if mv2 is None: return None
    lon_axis1 = lonAxis(mv1)
    lon_axis2 = lonAxis(mv2)
    if len(lon_axis1)<=len(lon_axis2):
        lon_axis = lon_axis1
        mv = mv1
    else:
        lon_axis = lon_axis2
        mv = mv2
    lonmv = cdms2.createVariable( lon_axis[:], axes=[lon_axis], id='lon',
                                  attributes={'units':lon_axis.units} )
    return lonmv

def levvar_min( mv1, mv2 ):
    """returns a transient variable which is dimensioned as whichever of mv1, mv2
    has the fewest level points but whose values are the levels"""
    if mv1 is None: return None
    if mv2 is None: return None
    lev_axis1 = levAxis(mv1)
    lev_axis2 = levAxis(mv2)
    if len(lev_axis1)<=len(lev_axis2):
        lev_axis = lev_axis1
        mv = mv1
    else:
        lev_axis = lev_axis2
        mv = mv2
    levmv = cdms2.createVariable( lev_axis[:], axes=[lev_axis], id='levels',
                                  attributes={'units':lev_axis.units} )
    return levmv

def interp2( newaxis1, mv ):
    """interpolates a variable mv along its second axis, normally latitude,
    so as to match the new axis (which should be coarser, i.e. fewer points),
    and returns a numpy array of the interpolated values.
    The first axis is normally levels, and isn't expected to be very large (usually <20; surely <50)
    There shall be no more than two axes."""
    missing = mv.get_fill_value()
    axes = allAxes(mv)
    if len(newaxis1[:])>len(axes[1][:]): return mv
    new_vals = numpy.ma.masked_all( ( len(axes[0]), len(newaxis1[:]) ) )
    for i in range(len( axes[0] )):
        new_vals[i,:] = numpy.interp(  newaxis1[:], axes[1][:], mv[i,:], left=missing, right=missing )
        # numpy.interp loses the mask, and I want to propagate it!  But we can separately interpolate
        # the mask - which numpy.interp treats False as 0, True as 1:
        new_vals.mask[i,:] = ( numpy.interp( newaxis1[:], axes[1][:], mv.mask[i,:], left=missing,
                                             right=missing ) )>0
    return new_vals

def aminusb0( mv1, mv2 ):
    """ returns mv1[0,]-mv2[0,]; they should be dimensioned alike.  Attributes will be fixed up where I know how."""
    mv = mv1[0,] - mv2[0,]
    if hasattr(mv,'long_name'):
        if mv.long_name==mv1.long_name:  # They're different, shouldn't have the same long_name
            mv.long_name = ''
    return mv

def aminusb_ax2( mv1, mv2 ):
    """returns a transient variable representing mv1-mv2, where mv1 and mv2 are variables with
    exactly two axes, with the first axis the same for each (but it's ok to differ only in units,
    which could be converted).
    To perform the subtraction, one of the variables is linearly interpolated in its second
    dimension to the second axis of the other.
    The axis used will be the coarsest (fewest points) of the two axes."""
    if hasattr(mv1,'units') and hasattr(mv2,'units') and mv1.units!=mv2.units:
        print "WARING: aminusb_ax2 is subtracting variables with different units!",mv1,mv1
    axes1 = allAxes(mv1)
    axes2 = allAxes(mv2)
    # TO DO: convert, interpolate, etc. as needed to accomodate differing first axes.
    # But for now, we'll just check a bit ...
    ax1=axes1[0]
    ax2=axes2[0]
    if ax1.shape!=ax2.shape:
        print "ERROR aminusb_ax2 requires same axes, but shape differs:",ax1.shape,ax2.shape
        print "ax1,ax2"
        return None
    if hasattr(ax1,'units') and hasattr(ax2,'units') and ax1.units!=ax2.units:
        if ax1.units=='mb':
            ax1.units = 'mbar' # udunits uses mb for something else
        if ax2.units=='mb':
            ax2.units = 'mbar' # udunits uses mb for something else
        tmp = udunits(1.0,ax2.units)
        s,i = tmp.how(ax1.units)  # will raise an exception if conversion not possible
        # crude substitute for a real units library:
        #if not (ax1.units=='mb' and ax2.units=='millibars') and\
        #   not (ax1.units=='millibars' and ax2.units=='mb'):
        #    print "ERROR aminusb_ax2 requires same axes, but units differ:",ax1.units,ax2,units
        #    print "ax1,ax2"
        #    return None
    ab_axes = [ax1]
    if len(axes1[1])<=len(axes2[1]):
        a = mv1
        b = interp2( axes1[1], mv2 )
        ab_axes.append(axes1[1])
    else:
        a = interp2( axes2[1], mv1 )
        b = mv2
        ab_axes.append(axes2[1])
    aminusb = a - b
    aminusb.id = mv1.id
    aminusb.initDomain( ab_axes )
    return aminusb

def reconcile_units( mv1, mv2 ):
    if hasattr(mv1,'units') and hasattr(mv2,'units') and mv1.units!=mv2.units:
        if mv1.units=='mb':
            mv1.units = 'mbar' # udunits uses mb for something else
        if mv2.units=='mb':
            mv2.units = 'mbar' # udunits uses mb for something else
        if mv1.units=='mb/day':
            mv1.units = 'mbar/day' # udunits uses mb for something else
        if mv2.units=='mb/day':
            mv2.units = 'mbar/day' # udunits uses mb for something else
        tmp = udunits(1.0,mv2.units)
        s,i = tmp.how(mv1.units)  # will raise an exception if conversion not possible
        mv2 = s*mv2 + i
        mv2.units = mv1.units
    return mv1, mv2

def aminusb_2ax( mv1, mv2 ):
    """returns a transient variable representing mv1-mv2, where mv1 and mv2 are variables, normally
    transient variables, which depend on exactly two axes, typically lon-lat.
    To perform the subtraction, the variables will be interpolated as necessary to the axes
    which are minimal (fewest points) in each direction.
    Note that if mv1 _or_ mv2 have a missing value at index i, then the return value (mv1-mv2)
    will also have a missing value at index i.
    """
    return mv2
    mv1, mv2 = reconcile_units( mv1, mv2 )
    missing = mv1.get_fill_value()
    axes1 = allAxes(mv1)
    axes2 = allAxes(mv2)
    if axes1 is None or axes2 is None: return None
    if len(axes1)!=2: print "ERROR @1, wrong number of axes for aminusb_2ax",axes1
    if len(axes2)!=2: print "ERROR @2, wrong number of axes for aminusb_2ax",axes2
    if len(axes1[0])==len(axes2[0]):
        # Only axis2 differs, there's a better way...
        return aminusb_ax2( mv1, mv2 )
    if len(axes1[0])<=len(axes2[0]):
        if len(axes1[1])<=len(axes2[1]):
            mv1new = mv1
            # Interpolate mv2 from axis2 to axis1 in both directions.  Use the CDAT regridder.
            grid1 = mv1.getGrid()
            mv2new = mv2.regrid(grid1)
        else:
            # Interpolate mv1 from axis1[1] to axis2[1]
            # Interpolate mv2 from axis2[0] to axis1[0]
            print "ERROR @3, aminusb_2ax IS NOT FINISHED"
            return None
    else:
        if len(axes1[1])<=len(axes2[1]):
            # Interpolate mv1 from axis1[0] to axis2[0]
            # Interpolate mv2 from axis2[1] to axis1[1]
            print "ERROR @4, aminusb_2ax IS NOT FINISHED"
            return None
        else:
            mv2new = mv2
            # Interpolate mv2 from axis2 to axis1 in both directions.  Use the CDAT regridder.
            grid2 = mv2.getGrid()
            mv1new = mv1.regrid(grid2)
    aminusb = mv1new - mv2new
    aminusb.id = mv1.id
    return aminusb

def aminusb_1ax( mv1, mv2 ):
    """returns a transient variable representing mv1-mv2, where mv1 and mv2 are variables, normally
    transient variables, which are required to depend only one axis.
    To perform the subtraction, one of the variables is linearly interpolated to the axis of
    the other.    The axis used will be the coarsest (fewest points) of the two axes.
    Note that if mv1 _or_ mv2 have a missing value at index i, then the return value (mv1-mv2)
    will also have a missing value at index i.
    """
    mv1, mv2 = reconcile_units( mv1, mv2 )
    if hasattr(mv1,'units') and hasattr(mv2,'units') and mv1.units!=mv2.units:
        print "WARNING: aminusb_1ax1 is subtracting variables with different units!",mv1,mv1
    if mv1 is None or mv2 is None: return None
    missing = mv1.get_fill_value()
    axis1 = allAxes(mv1)[0]
    axis2 = allAxes(mv2)[0]
    if len(axis1)<=len(axis2):
        a = mv1
        b = numpy.interp( axis1[:], axis2[:], mv2[:], left=missing, right=missing )
    else:
        a = numpy.interp( axis2[:], axis1[:], mv1[:], left=missing, right=missing )
        b = mv2
    aminusb = a - b
    aminusb.id = mv1.id
    return aminusb

def timeave_seasonal( mv, seasons=seasonsyr ):
    """Returns time averages of the cems2 variable mv.  The average is comuted only over times which
    lie in the specified season(s).  The returned variable has the same number of
    dimensions as mv, but the time axis  has been reduced to the number of seasons requested.
    The seasons are specified as an object of type cdutil.times.Seasons, and defaults to the whole
    year.
    """
    return seasons.climatology(mv)

def timeave_old( mv ):
    """Returns a time average of the cdms2 variable mv.
    mv is a cdms2 variable, assumed to be time-dependent and indexed as is usual for CF-compliant
    variables, i.e. mv(time,...).
    What's returned is a numpy array, not a cdms2 variable.  (I may change this in the future).
    """
    # I haven't thought yet about how missing values would work with this...
    # If time intervals be unequal, this will have to be changed...
    sh = mv.shape    # e.g. [312,90,144] for t,lat,lon
    n = sh[0]
    # BTW, this is the size of everything else:
    # n2 = reduce( operator.mul, sh[1:] ) # e.g. 90*144=12960
    mvta = numpy.sum( mv.__array__(), axis=0 )
    mvta /= n
    return mvta

def minmin_maxmax( *args ):
    """returns a TransientVariable containing the minimum and maximum values of all the variables
    provided as arguments"""
    rmin = min( [ mv.min() for mv in args ] )
    rmax = max( [ mv.max() for mv in args ] )
    rmv = cdms2.createVariable( [rmin,rmax] )
    return rmv

def delete_singleton_axis( mv, vid=None ):
    """If mv depends on an axis with just one value, create a copy of mv without that axis, and
    without the corresponding data dimension.  Normally this happens when time has been averaged
    out, but there is still a one-valued time axis left (thus one would normally use id='time').
    You can specify the axis id if there might be more than one singleton."""
    axes = allAxes(mv)
    saxis = None
    si = None
    for i in range(len(axes)):
        if len(axes[i])==1 and (vid==None or axes[i].id==vid):
            saxis = axes[i]
            si = i
            del axes[si]
            break
    if saxis==None: return mv
    data = ma.copy( mv.data )
    if numpy.version.version >= '1.7.0':
        data = ma.squeeze( data, axis=si )
    else:
        data = ma.squeeze( data )   # let's hope that there's only one singleton!
    mvnew = cdms2.createVariable ( data, axes=axes, id=mv.id )
    if hasattr(mv,'units'): mvnew.units = mv.units
    return mvnew

def common_axes( mv1, mv2 ):
    """Not much tested - I decided against doing overlapping line plots this way.
    The input arguments are two variables (cdms2 MVs, normally TransientVariables), with whatever
    compatibility is needed for this function to work.  New axes are computed which can be used for
    both variables.  These axes are returned as a list of tuples, each containing one new axis and
    index information."""
    axes1 = [a[0] for a in mv1.getDomain()]
    axes2 = [a[0] for a in mv2.getDomain()]
    if len(axes1)!=len(axes2):
        print "ERROR.  common_axes requires same number of axes in",mv1," and",mv2
        return None
    axes3 = []
    for i in range(len(axes1)):
        axes3.append(common_axis( axes1[i], axes2[i] ))
    return axes3

def common_axis( axis1, axis2 ):
    """Not much tested - I decided against doing overlapping line plots this way.
    The input arguments are two axes (AbstractAxis class), as compatible as necessary for the
    following to be sensible.  This function has 3 return values.  It returns a TransientAxis which
    includes all the points of the input axes.  It may be one of the inputs.  It also returs
    index information from which one can determine whether a point of the new axis came from
    axis1 or axis2 or both."""
    if hasattr( axis1, 'units' ):
        units1 = axis1.units.lower().replace(' ','_')
        if axis1.isTime():
            axis1.toRelativeTime( units1 )  #probably will change input argument
    else:
        units1 = None
    if hasattr( axis2, 'units' ):
        units2 = axis2.units.lower().replace(' ','_')
    else:
        units2 = None
    if units1!=None and units2!=None and units1 != units2:
        if axis1.isTime() and axis2.isTime():
            axis2.toRelativeTime( units1, axis1.getCalendar() )  #probably will change input argument
        else:
            print "ERROR.  common_axis does not yet support differing units",axis1.units," and ",axis2.units
            return None
    if axis1.isTime() or axis2.isTime():
        if not axis2.isTime() or not axis1.isTime():
            print "ERROR.  In common_axis, one axis is time, not the other"
            return None
        if not axis1.calendar==axis2.calendar:
            print "ERROR.  common_axis does not yet support differing calendars."
        if len(axis1)==1 and len(axis2)==1:
            # There's just one time value, probably from averaging over time.  The time value is meaningless
            # but it would be messy to have two.
            return (axis1,[0],[0])

    # to do: similar checks using isLatitude and isLongitude and isLevel <<<<<<
    # Also, transfer long_name, standard_name, axis attributes if in agreement;
    # units and calendar attributes should always be transferred if present.
    # Also to do: use bounds if available
    a12 = numpy.concatenate( [ axis1.getData(), axis2.getData() ] )
    a3, a12indexina3 = numpy.unique( a12, return_inverse=True )
    #... a3 has only unique indices and is sorted (unfortunately, uniqueness is based on exact identity,
    # not to some numerical tolerance).  For an i index into a12 (thus 0<=i<len(axis1)+len(axis2),
    # j is an index into a3 such that, if a12indexina3[i]==j, then a1[i]==a3[j].
    a1indexina3 = a12indexina3[0:len(axis1)]
    a2indexina3 = a12indexina3[len(axis1):len(axis1)+len(axis2)]

    if hasattr(axis1,'id') and hasattr(axis2,'id') and axis1.id==axis2.id :
        vid = axis1.id
    else:
        vid = None
    axis3 = cdms2.createAxis( a3, bounds=None, id=vid )
    axis3.units = units1
    return (axis3,a1indexina3,a2indexina3)

def convert_axis( mv, axisold, axisindnew ):
    """Not much tested - I decided against doing overlapping line plots this way.
    Returns a TransientVaraible made by replacing an axis axisold of a TransientVariable mv with
    a new axis.  The new axis will have all points of the old axis, but may have more, thus
    requiring the new variable to have more missing data.
    The variable axisnindew is a 2-tuple, containing the new axis and index information describing
    which elements came from the old axis.  In terms of common_axis(), it is (axis3,a1indexina3)
    or (axis3,a2indexina3)."""
    (axisnew, indexina3) = axisindnew
    axes = allAxes(mv)
    kold = None
    for k in range(len(axes)):
        if axes[k]==axisold: kold=k
    if kold==None:
        print "ERROR. convert_axis cannot find axis",axisold," in variable",mv
    if len(axisold)==len(axisnew):
        mv.setAxis( kold, axisnew )
        return
    # Here's what we would do in 1-D:
    # newdata = ma.ones(len(axisnew))*mv.missing_value  # Note that a FileVariable's missing_value is a tuple.
    # for i in range(len(axisold)):
    #     newdata[ indexina3[i] ] = ma[i]
    # newmv = cdms2.createVariable( newdata, id=mv.id )
    # >1-D is the same idea, but more dimensions are coming along for the ride,
    # making it more complicated...
    shape0 = mv.shape
    shape0[kold] = len(axisnew)
    newdata = ma.ones(shape0)*mv.missing_value  # Note that a FileVariable's missing_value is a tuple.
    # We want to copy ma to newdata - except that we need indirect indexing for the kold-th axis.
    # There seems to be nothing in numpy for treating one axis differently from the rest
    # (except for ellipsis, but it makes sense to use only one ellipsis and we would need two here).
    # The following will do the job.  It would be very slow for an array with many big dimensions,
    # but the arrays here have already been reduced for graphics; the index sets will be small or
    # empty...
    ranges = map( range, shape0[0:kold] )
    for i in range(len(axisold)):
        for idx in apply(itertools.product,ranges):
            idx = idx + [indexina3(i)] + [Ellipsis]
            idxo = idx + [i] + [Ellipsis]
            newdata[ tuple(idx) ] = mv[idxo]
    newmv = cdms2.createVariable( newdata, id=mv.id )



class reduced_variable(ftrow):
    """Specifies a 'reduced variable', which is a single-valued part of an output specification.
    This would be a variable(s) and its domain, a reduction function, and perhaps
    an axis or two describing the domain after applying the reduction function.
    Output may be based on one or two of these objects"""
    # The reduction function should take just one parameter, the data to be reduced.
    # In reality we will have a more generic function, and some additional parameters.
    # So this reduction function will typically be specified as a lambda expression, e.g.
    # (lambda mv: return zonal_mean( mv, sourcefile, -20, 20 )
    def __init__( self, fileid=None, variableid='', timerange=None,\
                      latrange=None, lonrange=None, levelrange=None,\
                      reduced_var_id=None,\
                      reduction_function=(lambda x,vid=None: x),\
                      filetable=None, axes=None
                  ):
        ftrow.__init__( self, fileid, variableid, timerange, latrange, lonrange, levelrange )
        self._reduction_function = reduction_function
        self._axes = axes
        if reduced_var_id is None:
            self._vid = ""
        else:
            self._vid = reduced_var_id
        if filetable==None:
            print "ERROR.  No filetable specified for reduced_variable instance",variableid
        self._filetable = filetable

    def extract_filefamilyname( self, filename ):
        """From a filename, extracts the first part of the filename as the possible
        name of a family of files; e.g. from 'ts_Amon_bcc-csm1-1_amip_r1i1p1_197901-200812.nc'
        extract and return 'ts_Amon_bcc-csm1-1_amip_r1i1p1'.  To distinguish between the
        end of a file family name and the beginning of the file-specific part of the filename,
        we look for an underscore and two numerical digits, e.g. '_19'."""
        matchobject = re.search( r"^.*_\d\d", filename )
        if matchobject is None:
            return filename
        else:
            familyname = filename[0:(matchobject.end()-3)]
            return familyname        

    def reduce( self, vid=None ):
        """Finds and opens the files containing data required for the variable,
        Applies the reduction function to the data, and returns an MV.
        When completed, this will treat missing data as such.
        At present only CF-compliant files are supported."""
        if vid is None:
            vid = self._vid
        rows = self._filetable.find_files( self.variableid, time_range=self.timerange,
                                           lat_range=self.latrange, lon_range=self.lonrange,
                                           level_range=self.levelrange )
        if rows==None or len(rows)<=0:
            # this belongs in a log file:
            print "ERROR no data found for reduced variable",self.variableid
            print "in",self.timerange, self.latrange, self.lonrange, self.levelrange
            print "filetable is",self._filetable
            return None

        # To make it even easier on the first cut, I won't worry about missing data and
        # anything else inconvenient, and I'll assume CF compliance.
        files = list(set([r.fileid for r in rows]))
        if len(files)>1:
            # Piece together the data from multiple files.  That's what cdscan is for...
            # One problem is there may be more than one file family in the same
            # directory!  If we see more than one at this point, the user wasn't
            # careful in his specifications.  We'll just have to choose one.
            famdict = { f:self.extract_filefamilyname(f) for f in files }
            families = list(set([ famdict[f] for f in files ]))
            families.sort(key=len)  # a shorter name is more likely to be what we want
            if len(families)==0:
                print "ERROR.  No data to reduce.  files[0]=:",files[0]
                return None
            elif len(families)>1:
                print "WARNING: ",len(families)," file families found, will use the first one:",families
            fam = families[0]

            # We'll run cdscan to combine the multiple files into one logical file.
            # To save (a lot of) time, we'll re-use an xml file if a suitable one already exists.
            # To do this safely, incorporate the file list (names,lengths,dates) into the xml file name.
            famfiles = [f for f in files if famdict[f]==fam]
            famfiles.sort()   # improves consistency between runs
            file_list = '-'.join(
                [ f+'size'+str(os.path.getsize(f))+'mtime'+str(os.path.getmtime(f))\
                      for f in famfiles ] )
            csum = hashlib.md5(file_list).hexdigest()
            xml_name = fam+'_cs'+csum+'.xml'
            if os.path.isfile( xml_name ):
                files = [ xml_name ]

        if len(files)>1:
            famfiles = [f for f in files if famdict[f]==fam]
            # Normally when we get here, it's because data has been divided by time among
            # several files.  So when cdscan puts it all back together, it needs the time
            # units.  If the time variable is named 'time' and has a valid 'units'
            # attribute, we're fine; otherwise we're in trouble.  But for some AMWG obs
            # data which I have, the time units may be found in the long_name attribute.
            # The -e option will normally be the way to fix it up, but maybe the -r option
            # could be made to work.
            
            # I know of no exception to the rule that all files in the file family keep their
            # units in the same place; so find where they are by checking the first file.
            f = cdms2.open( famfiles[0] )
            time_units = f['time'].units
            if type(time_units) is str and len(time_units)>3:
                # cdscan can get time units from the files; we're good.
                f.close()
                cdscan_line = 'cdscan -q '+'-x '+xml_name+' '+' '.join(famfiles)
            else:
                # cdscan needs to be told what the time units are.  I'm betting that all files
                # use the same units.  I know of cases where they all have different units (e.g.,
                # GISS) but in all those cases, the units attribute is used properly, so we don't
                # get here.
                # Another problem is that units stuck in the long_name sometimes are
                # nonstandard.  So fix them!
                if hasattr(f['time'],'long_name'):
                    time_units = f['time'].long_name
                else:
                    time_units = 'days'  # probably wrong but we can't go on without something
                    # Usually when we get here it's a climatology file where time is meaningless.
                f.close()
                if type(time_units) is str and len(time_units)>1 and (
                    time_units.find('months')==0 or time_units.find('days')==0 or
                    time_units.find('hours')==0 ):
                    time_units = fix_time_units( time_units )
                    cdscan_line = 'cdscan -q '+'-x '+xml_name+' -e time.units="'+time_units+'" '+\
                        ' '.join(famfiles)
                else:
                    print "WARNING, cannot find time units; will try to continue",famfiles[0]
                    cdscan_line = 'cdscan -q '+'-x '+xml_name+' -e time.units="'+time_units+'" '+\
                        ' '.join(famfiles)
            print "cdscan_line=",cdscan_line
            proc = subprocess.Popen([cdscan_line],shell=True)
            proc_status = proc.wait()
            if proc_status!=0: print "ERROR: cdscan terminated with",proc_status
            f = cdms2.open( xml_name )
        else:
            # the easy case, just one file has all the data on this variable
            f = cdms2.open(files[0])
        fcf = get_datafile_filefmt(f)
        reduced_data = self._reduction_function( f(self.variableid), vid=vid )
        if reduced_data is not None:
            reduced_data._vid = vid
        f.close()
        return reduced_data





