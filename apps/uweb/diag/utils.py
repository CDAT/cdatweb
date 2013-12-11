import os,sys
import metrics.fileio.findfiles
from metrics.diagnostic_groups import *
import metrics.frontend.uvcdat
def get_filetable1():
    path1="/export/leung25/Downloads/cam_output/test.xml"
    tmppath="/export/leung25/tmp"
    if not os.path.exists(tmppath):
        os.makedirs(tmppath)
    datafiles = metrics.fileio.findfiles.dirtree_datafiles( path1 )
    filetable1 = datafiles.setup_filetable( tmppath, "model" )
    print "filetable1=", filetable1
    return filetable1

def get_filetable2():
    path2="/export/leung25/Downloads/obs_data"
    datafile2 = metrics.fileio.findfiles.dirtree_datafiles( path2)
    tmppath="/export/leung25/tmp"
    if not os.path.exists(tmppath):
        os.makedirs(tmppath)
    filetable2=datafile2.setup_filetable(tmppath,"obs")
    print "filetable2=", filetable2
    return filetable2

def get_input_parameter(package, plot_set, seasonID, variableID):
    dg_menu=diagnostics_menu()[str(package)]()
    plot_set_obj=dg_menu.list_diagnostic_sets()[str(plot_set)]
    filetable1=get_filetable1()
    filetable2=get_filetable2()
    return plot_set_obj,filetable1,filetable2, variableID, seasonID


