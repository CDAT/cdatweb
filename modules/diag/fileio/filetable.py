#!/usr/local/uvcdat/1.3.1/bin/python

# Set up and index a table whose entries will be something like
#   file_id,  variable_id,  time_range,  lat_range,  lon_range,  level_range
# subject to change!

import sys, os, cdms2, pprint

class drange:
   def __init__( self, low=None, high=None, units=None ):
      if low  is None: low = float('-inf')
      if high is None: high = float('inf')
      self.lo = low
      self.hi = high
      self.units = units
   def overlaps_with( self, range2 ):
      if range2==None:
         # None means everything, units don't matter
         return True
      elif range2.lo==float('-inf') and range2.hi==float('inf'):
         # Everything, units don't matter
         return True
      elif self.units!=range2.units and self.units!=None and range2.units!=None:
         # >>> TO DO >>>> units conversion, and think more about dealing with unspecified units
         return False
      else:
         return self.hi>range2.lo and self.lo<range2.hi
   def __repr__(self):
      return "drange %s to %s %s"%(self.lo,self.hi,self.units)
       
class ftrow:
    """This class identifies a file and contains the information essential to tell
    whether the file has data we want to graph: a variable and its domain information.
    There will be no more than that - if you want more information you can open the file.
    If the file has several variables, there will be several rows for the file."""
    # One can think of lots of cases where this is too simple, but it's a start.
    def __init__( self, fileid, variableid, timerange, latrange, lonrange, levelrange=None ):
        self.fileid = fileid          # file name
        self.variableid = variableid  # variable name
        if timerange is None:
           self.timerange = drange()
        else:
           self.timerange = timerange
        if latrange is None:
           self.latrange = drange()
        else:
           self.latrange = latrange
        if lonrange is None:
           self.lonrange = drange()
        else:
           self.lonrange = lonrange
        if levelrange is None:
           self.haslevel = False
           self.levelrange = drange()
        else:
           self.haslevel = True
           self.levelrange = levelrange
    def __repr__(self):
       if self.fileid is None:
          filerepr = "<no file>"
       else:
          filerepr = os.path.basename(self.fileid)
       return "\n(ftrow: ..%s %s domain:\n   %s %s %s)"%(
          filerepr, self.variableid,\
             self.timerange.__repr__(), self.latrange.__repr__(), self.lonrange.__repr__() )


def get_datafile_filefmt( dfile, get_them_all=False ):
    """dfile is an open datafile.  If the file type is recognized,
    then this will return an object with methods needed to support that file type."""
    if hasattr(dfile,'source') and ( dfile.source[0:3]=='CAM' or dfile.source[0:4]=='CCSM'\
           or dfile.source[0:4]=='CESM' ):
       return NCAR_filefmt( dfile, get_them_all )
       # Note that NCAR Histoy Tape files are marked as supporting the CF Conventions
       # and do so, but it's minimal, without most of the useful CF features (e.g.
       # where are bounds for the lat axis?).
       # The same applies to the dataset xml file produced by cdscan from such files.
    if hasattr(dfile,'Conventions') and dfile.Conventions[0:2]=='CF':
       # Really this filefmt assumes more than CF-compliant - it requires standard
       # but optional features such as standard_name and bounds attribures.  Eventually
       # I should put in a check for that.
       return CF_filefmt( dfile )
    else:
       return NCAR_filefmt( dfile, get_them_all )
       # Formerly this was "return Unknown_filefmt()" but I have some obs data from NCAR
       # which has no global attributes which would tell you what kind of file it is.
       # Nevertheless the one I am looking at has lots of clues, e.g. variable and axis names.

class basic_filetable:
    """Conceptually a file table is just a list of rows; but we need to attach some methods,
    which makes it a class.  Moreover, indices for the table are in this class.
    Different file types will require different methods,
    and auxiliary data."""

    def __init__( self, filelist, ftid='', get_them_all=False ):
        """filelist is a list of strings, each of which is the path to a file"""
        self._table = []     # will be built from the filelist, see below
        # We have two indices, one by file and one by variable.
        # the value is always a list of rows of the table.
        self._fileindex = {} # will be built as the table is built
        # The variable index is based on the CF standard name.  Why that?  We have to standardize
        # the variable in some way in order to have an API to the index, and CF standard names
        # cover just about anything we'll want to plot.  If something is missing, we'll need our
        # own standard name list.
        self._varindex = {} # will be built as the table is built
        #print "filelist=",filelist,type(filelist)
        self._filelist = filelist # just used for __repr__
        if filelist is None: return
        self._id = ftid
        for filep in filelist.files:
            self.addfile( filep, get_them_all )
    def __repr__(self):
       return 'filetable from '+str(self._filelist)
    def full_repr(self):
       return 'filetable from '+str(self._filelist)+'\n'+self._table.__repr__()
    def sort(self):
       """in-place sort keyed on the file paths"""
       self._table.sort(key=(lambda ftrow: ftrow.fileid))
       return self
    def nrows( self ):
       return len(self._table)
    def addfile( self, filep, get_them_all=False ):
        """Extract essential header information from a file filep,
        and put the results in the table.
        filep should be a string consisting of the path to the file."""
        fileid = filep
        try:
           dfile = cdms2.open( fileid )
        except cdms2.error.CDMSError as e:
           # probably "Cannot open file", but whatever the problem is, don't bother with it.
           return
        filesupp = get_datafile_filefmt( dfile, get_them_all )
        vars = filesupp.interesting_variables()
        if len(vars)>0:
            timerange = filesupp.get_timerange()
            latrange = filesupp.get_latrange()
            lonrange = filesupp.get_lonrange()
            levelrange = filesupp.get_levelrange()
            for var in vars:
                variableid = var
                varaxisnames = [a[0].id for a in dfile[var].domain]
                if 'time' in varaxisnames:
                   timern = timerange
                else:
                   timern = None
                if 'lat' in varaxisnames:
                   latrn = latrange
                else:
                   latrn = None
                if 'lon' in varaxisnames:
                   lonrn = lonrange
                else:
                   lonrn = None
                if 'lev' in varaxisnames:
                   levrn = levelrange
                else:
                   levrn = None
                newrow = ftrow( fileid, variableid, timern, latrn, lonrn, levrn )
                self._table.append( newrow )
                if fileid in self._fileindex.keys():
                    self._fileindex[fileid].append(newrow)
                else:
                    self._fileindex[fileid] = [newrow]
                if variableid in self._varindex.keys():
                    self._varindex[variableid].append(newrow)
                else:
                    self._varindex[variableid] = [newrow]
        dfile.close()
    def find_files( self, variable, time_range=None,
                    lat_range=None, lon_range=None, level_range=None ):
       """This method is intended for creating a plot.
       This finds and returns a list of files needed to cover the supplied variable and time and
       space ranges.
       The returned list may contain more or less than requested, but will be the best available.
       The variable is a string, containing as a CF standard name, or equivalent.
       For ranges, None means you want all values."""
       if variable not in self._varindex.keys():
          return None
       candidates = self._varindex[ variable ]
       found = []
       for ftrow in candidates:
          if time_range.overlaps_with( ftrow.timerange ) and\
                 lat_range.overlaps_with( ftrow.latrange ) and\
                 lon_range.overlaps_with( ftrow.lonrange ) and\
                 level_range.overlaps_with( ftrow.levelrange ):
             found.append( ftrow )
       return found
    def list_variables(self):
       vars = list(set([ r.variableid for r in self._table ]))
       vars.sort()
       return vars
    def list_variables_with_levelaxis(self):
       vars = list(set([ r.variableid for r in self._table if r.haslevel]))
       vars.sort()
       return vars
            
class basic_filefmt:
    """Children of this class contain methods which support specific file types,
    and are used to build the file table.  Maybe later we'll put here methods
    to support other functionality."""
    def get_timerange(self): return None
    def get_latrange(self): return None
    def get_lonrange(self): return None
    def get_levelrange(self): return None
    def interesting_variables(self): return []
    def variable_by_stdname(self,stdname): return None

class Unknown_filefmt(basic_filefmt):
    """Any unsupported file type gets this one."""

class NCAR_filefmt(basic_filefmt):
   """NCAR History Tape format, used by CAM,CCSM,CESM.  This class works off a derived
   xml file produced with cdscan."""
   def __init__(self,dfile, get_them_all=False):
      """dfile is an open file.  It must be an xml file produced by cdscan,
      combining NCAR History Tape format files."""
      self._dfile = dfile
      if get_them_all:
         self._all_interesting_names = self._dfile.variables.keys()
      else:
         self._all_interesting_names = [
            'hyam', 'hybm', 'CLDTOT',
            'T', 'TREFHT', 'PRECT', 'PS', 'PSL', 'Z500', 'ORO', 'QFLX',
            'FSNS', 'FLNS', 'FLUT', 'FSNTOA', 'FLNT', 'FSNT', 'SHFLX', 'LHFLX', 'OCNFRAC'
            ] 

   def get_timerange(self):
      if 'time' not in self._dfile.axes:
         return None
      timeax = self._dfile.axes['time']
      if hasattr( timeax, 'bounds' ):
         time_bnds_name = timeax.bounds
         if self._dfile[time_bnds_name] is not None:
            lo = self._dfile[time_bnds_name][0][0]
            hi = self._dfile[time_bnds_name][-1][1]
         else:
            lo = timeax[0]
            hi = timeax[-1]
      else:
         lo = timeax[0]
         hi = timeax[-1]
      if hasattr( timeax, 'units' ):
         units = timeax.units
      elif hasattr( timeax, 'long_name' ) and timeax.long_name.find(' since ')>1:
         units = timeax.long_name   # works at least sometimes
      else:
         units = None
      return drange( lo, hi, units )
   def get_latrange(self):
      # uses center points because the axis doesn't have a bounds attribute
      if 'lat'  in self._dfile.axes:
         lo = self._dfile.axes['lat'][0]
         hi = self._dfile.axes['lat'][-1]
         units = self._dfile.axes['lat'].units
      else:
         lo = None
         hi = None
         units = None
      return drange( lo, hi, units )
   def get_lonrange(self):
      # uses center points because the axis doesn't have a bounds attribute
      if 'lon' in self._dfile.axes:
         lo = self._dfile.axes['lon'][0]
         hi = self._dfile.axes['lon'][-1]
         units = self._dfile.axes['lon'].units
      else:
         lo = None
         hi = None
         units = None
      return drange( lo, hi, units )
   def get_levelrange(self):
      # uses interface points, which are bounds on the level centers
      if 'ilev' in self._dfile.axes.keys():
         lo = self._dfile.axes['ilev'][0]
         hi = self._dfile.axes['ilev'][-1]
         units = self._dfile.axes['ilev'].units
      elif 'lev' in self._dfile.axes.keys():
         lo = self._dfile.axes['lev'][0]
         hi = self._dfile.axes['lev'][-1]
         units = self._dfile.axes['lev'].units
      else:
         return None
      return drange( lo, hi, units )
   def interesting_variables(self):
      """returns a list of interesting variables in the NCAR History Tape file.
      The name returned will be a standard name if known, otherwise (and usually)
      the actual variable name."""
      iv = []
      for var in self._dfile.variables.keys():
         if len(self._dfile.variables[var].getAxisList())>=3:
            iv.append(var)
         if var in self._all_interesting_names:
            iv.append(var)
         elif hasattr(self._dfile[var],'original_name') and\
                self._dfile[var].original_name in self._all_interesting_names:
            iv.append(var)
      return iv
   def variable_by_stdname(self,stdname):
      """returns the variable name for the given standard name if known; otherwise
      if the variable be interesting, the name itself is returned."""
      for var in self._dfile.variables.keys():
         standard_name = getattr( self._dfile[var], 'standard_name', None )
         if standard_name==stdname:
            return var
         elif var==stdname and var in self._all_interesting_names:
            return var
         else:
            original_name = getattr( self._dfile[var], 'original_name', None )
            if var==stdname and original_name in self._all_interesting_names:
               return var

      # For now, just return the input name, it's better than nothing - I haven't yet tried
      # seriously to use the standard_name concept for NCAR files
      return stdname
      #return None

class CF_filefmt(basic_filefmt):
    """NetCDF file conforming to the CF Conventions, and using useful CF featues
    such as standard_name and bounds."""
    def __init__(self,dfile):
        """dfile is an open file"""
        # There are many possible interesting variables!
        # As we add plots to the system, we'll need to expand this list:
        self._all_interesting_standard_names = [
            'cloud_area_fraction', 'precipitation_flux', 'surface_air_pressure',
            'surface_temperature' ]
        self._dfile = dfile
    def interesting_variables(self):
       """returns a list of interesting variables in the CF file.
       The standard_name, not the variable name, is what's returned."""
       iv = []
       # print "will check variables",self._dfile.variables.keys()
       for var in self._dfile.variables.keys():
          standard_name = getattr( self._dfile[var], 'standard_name', None )
          if standard_name!=None:
             print "  ",var," has standard name",standard_name
          #if standard_name in\
          #       self._all_interesting_standard_names:
          #   iv.append(standard_name)
          if standard_name is not None:
             iv.append(var)
       return iv
    def variable_by_stdname(self,stdname):
        for var in self._dfile.variables.keys():
           standard_name = getattr( self._dfile[var], 'standard_name', None )
           if standard_name==stdname:
              return var
        return None
    def get_timerange(self):
       if 'time' not in self._dfile.axes:
          return None
       if 'bounds' in self._dfile.axes['time'].__dict__:
          time_bnds_name = self._dfile.axes['time'].bounds
          lo = self._dfile[time_bnds_name][0][0]
          hi = self._dfile[time_bnds_name][-1][1]
       else:
          lo = self._dfile.axes['time'][0]
          hi = self._dfile.axes['time'][-1]
       units = self._dfile.axes['time'].units
       return drange( lo, hi, units )
    def get_latrange(self):
       if 'bounds' in self._dfile.axes['lat'].__dict__:
          lat_bnds_name = self._dfile.axes['lat'].bounds
          lo = self._dfile[lat_bnds_name][0][0]
          hi = self._dfile[lat_bnds_name][-1][1]
       else:
          lo = self._dfile.axes['lat'][0]
          hi = self._dfile.axes['lat'][-1]
       units = self._dfile.axes['lat'].units
       return drange( lo, hi, units )
    def get_lonrange(self):
       if 'bounds' in self._dfile.axes['lon'].__dict__:
          lon_bnds_name = self._dfile.axes['lon'].bounds
          lo = self._dfile[lon_bnds_name][0][0]
          hi = self._dfile[lon_bnds_name][-1][1]
       else:
          lo = self._dfile.axes['lon'][0]
          hi = self._dfile.axes['lon'][-1]
       units = self._dfile.axes['lon'].units
       return drange( lo, hi, units )
    def get_levelrange(self):
        levelaxis = None
        for axis_name in self._dfile.axes.keys():
            axis = self._dfile[axis_name]
            if hasattr( axis, 'positive' ):
                # The CF Conventions specifies this as a way to detect a vertical axis.
                levelaxis = axis
                break
        if levelaxis==None:
            return None
        lo = min( levelaxis[0], levelaxis[-1] )
        hi = max( levelaxis[0], levelaxis[-1] )
        units = levelaxis.units
        return drange( lo, hi, units )

if __name__ == '__main__':
   if len( sys.argv ) > 1:
      from findfiles import *
      datafiles = dirtree_datafiles( sys.argv[1] )
      filetable = basic_filetable( datafiles )
      print "filetable=", filetable.sort()
   else:
      print "usage: filetable.py root"

