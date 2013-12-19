#!/usr/local/uvcdat/2013-10-30/bin/python

# batch output - For now, writes data files for all plots we know how to make
# For now, inputs are hard-coded.
# TO DO: >>> separate plan_computation() from compute()
# >>>> How does the class design work with this? Improve as needed.

import hashlib, os, pickle, sys, os
from metrics import *
from metrics.fileio.filetable import *
from metrics.fileio.findfiles import *
from metrics.computation.reductions import *
from metrics.amwg import *
from metrics.amwg.derivations.vertical import *
from metrics.amwg.plot_data import plotspec, derived_var
from metrics.frontend.version import version
from metrics.amwg.derivations import *
from metrics.diagnostic_groups import *
from metrics.frontend.uvcdat import *
from pprint import pprint
import cProfile

path1 = os.path.join(os.environ["HOME"],'cam_output/b30.009.cam2.h0.06.xml')
#cmip5 test path1 = os.path.join(os.environ["HOME"],'cmip5/')
path2 = os.path.join(os.environ["HOME"],'obs_data')
#cmip5 test path2 = os.path.join(os.environ["HOME"],'cmip5/')
tmppth = os.path.join(os.environ['HOME'],"tmp")
outpath = os.path.join(os.environ['HOME'],"tmp","diagout")
if not os.path.exists(tmppth):
    os.makedirs(tmppth)
filt1 = None
#cmip5 test filt1 = f_or(f_startswith("p"),f_startswith("P"))
datafiles1 = dirtree_datafiles( path1, filt1 )
filetable1 = datafiles1.setup_filetable( tmppth, "model" )
filt2 = f_startswith("NCEP")
#cmip5 test filt2 = filt1
datafiles2 = dirtree_datafiles( path2, filt2 )
filetable2 = datafiles2.setup_filetable( tmppth, "obs" )

number_diagnostic_plots = 0
dm = diagnostics_menu()
for pname,pclass in dm.items():
    package = pclass()
    print "jfp package=",package
    sm = package.list_diagnostic_sets()
    for sname,sclass in sm.items():
        #if sclass.name != ' 6- Horizontal Vector Plots of Seasonal Means':
        #if sclass.name != ' 2- Line Plots of Annual Implied Northward Transport':
        if sclass.name != ' 3- Line Plots of  Zonal Means':
            continue   # for testing, only do one plot set
        print "jfp sname=",sname
        for seasonid in package.list_seasons():
            if seasonid != 'DJF':
                continue # for testing, only do one season
            print "jfp seasonid=",seasonid
            print "jfp variables=",package.list_variables( filetable1, filetable2, sname  )
            for varid in package.list_variables( filetable1, filetable2, sname  ):
                if varid!='TREFHT':
                    continue # for testing, only do one variable
                print "jfp varid=",varid
                proc = plotdata_run( sclass, filetable1, filetable2, varid, seasonid )
                res = plotdata_results( proc )
                #plot = sclass( filetable1, filetable2, varid, seasonid )
                #res = plot.compute()
                if res is not None: #>>> TO DO write res to a NetCDF file <<<<
                    number_diagnostic_plots += 1
                    #print plot
                    pprint( res )
                    for r in res:
                        print( r.write_plot_data( writer="JSON string" ) )
                        #r.write_plot_data(outpath)
print "total number of diagnostic plots generated =", number_diagnostic_plots
