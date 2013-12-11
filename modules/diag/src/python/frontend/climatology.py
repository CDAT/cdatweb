#!/usr/local/uvcdat/1.3.1/bin/python

# High-level functions to convert data to climatology files.
# These are, in my understanding, files which have a time-average of the original
# variables, with the time often restricted to a month or season.
# This is basically a simplified version of plot_data.py.

import cdms2, math
from metrics.fileio.filetable import *
from metrics.computation.reductions import *
from metrics.amwg.derivations.oaht import *
from metrics.amwg.derivations.ncl_isms import *
from metrics.amwg.derivations.vertical import *
from pprint import pprint

from plot_data import derived_var, plotspec
from cdutil.times import Seasons

class climatology_variable( reduced_variable ):
    def __init__(self,varname,filetable,seasonname='ANN'):
        if seasonname=='ANN':
            reduced_variable.__init__( self,
               variableid=varname, filetable=filetable,
               reduction_function=(lambda x,vid=None: reduce_time(x,vid=vid)) )
        else:
            season = cdutil.times.Seasons([seasonname])
            reduced_variable.__init__( self,
               variableid=varname, filetable=filetable,
               reduction_function=(lambda x,vid=None: reduce_time_seasonal(x,season,vid=vid)) )

def test_driver( path1, filt1=None ):
    """ Test driver for setting up data for plots"""
    datafiles1 = treeof_datafiles( path1, filt1 )
    print "jfp datafiles1=",datafiles1
    get_them_all = False  # Set True to get all variables in all specified files
    # Then you can call filetable1.list_variables to get the variable list.
    filetable1 = basic_filetable( datafiles1, get_them_all )
    print "jfp variable list from filetable1:", filetable1.list_variables()

    reduced_variables = { var+'_'+seas: climatology_variable(var,filetable1,seas)
                          for seas in ['ANN','DJF','JAN']
                          for var in filetable1.list_variables() }
    #                     for var in ['TREFHT','FLNT','SOILC']}
    #reduced_variables = {
    #    'TREFHT_ANN': reduced_variable(
    #        variableid='TREFHT', filetable=filetable1,
    #        reduction_function=(lambda x,vid=None: reduce_time(x,vid=vid)) ),
    #    'TREFHT_DJF': reduced_variable(
    #        variableid='TREFHT', filetable=filetable1,
    #        reduction_function=(lambda x,vid=None: reduce_time_seasonal(x,seasonsDJF,vid=vid)) ),
    #    'TREFHT_MAR': reduced_variable(
    #        variableid='TREFHT', filetable=filetable1,
    #        reduction_function=(lambda x,vid=None:
    #                                reduce_time_seasonal(x,Seasons(['MAR']),vid=vid)) )
    #    }

    varkeys = reduced_variables.keys()

    # Compute the value of every variable we need.
    varvals = {}
    # First compute all the reduced variables
    for key in varkeys:
        varvals[key] = reduced_variables[key].reduce()

    # Now use the reduced and derived variables to compute the plot data.
    for key in varkeys:
        var = reduced_variables[key]
        filename = key+"_test.nc"
        if varvals[key] is not None:
            g = cdms2.open( filename, 'w' )    # later, choose a better name and a path!
            g.write(varvals[key])
            g.close()

if __name__ == '__main__':
   if len( sys.argv ) > 1:
      from findfiles import *
      path1 = sys.argv[1]
      if len( sys.argv ) > 2 and sys.argv[2].find('filt=')==0:  # need to use getopt to parse args
          filt1 = sys.argv[2]
          test_driver(path1,filt1)
      else:
          test_driver(path1)
   else:
      print "usage: plot_data.py root"
