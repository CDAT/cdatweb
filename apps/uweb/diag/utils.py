import os,sys
import metrics.fileio.findfiles
from metrics.packages.diagnostic_groups import *
import metrics.frontend.uvcdat

from django.conf import settings

tmppath=os.path.join(os.environ["HOME"],"tmp")

import threading

class SingletonType(type):
    def __call__(cls, *args, **kwargs):
        try:
            return cls.__instance
        except AttributeError:
            cls.__instance = super(SingletonType, cls).__call__(*args, **kwargs)
            return cls.__instance

class ObsMenu(object):

    def __init__(self,diag_type):
        if diag_type=='AMWG':
            path2=settings.DIAG_AMWG_OBS_PATH
        elif diag_type=='LMWG':
            path2=settings.DIAG_LMWG_OBS_PATH
        print path2
        datafile2 = metrics.fileio.findfiles.dirtree_datafiles( path2)
        self.obs_menu=datafile2.check_filespec()

class TaskTracker(object):
    __metaclass__ = SingletonType

    def __init__(self):
        self.task_dict={}

    def add_task(self,taskID,task):
        self.task_dict[taskID]=task
    def del_task(self,taskID):
        if taskID in self.task_dict:
            del self.task_dict[taskID]
    def get_task(self,taskID):
        if taskID in self.task_dict:
            return self.task_dict[taskID]
        return None

def get_filetable1(diag_model):
    if diag_model=='CAM_HIRES':
        path1=settings.DIAG_HIRES_CAM_PATH
    elif diag_model=='CAM_LORES':
        path1=settings.DIAG_LORES_CAM_PATH
    elif diag_model=='CAM_OUTPUT':
        path1=settings.DIAG_CAM_OUTPUT_PATH
    elif diag_model=='CLM_HIRES':
        path1=settings.DIAG_HIRES_CLM_PATH
    elif diag_model=='CLM_LORES':
        path1=settings.DIAG_LORES_CLM_PATH
    elif diag_model=='CLM_OUTPUT':
        path1=settings.DIAG_CLM_OUTPUT_PATH
    if not os.path.exists(tmppath):
        os.makedirs(tmppath)
    datafiles = metrics.fileio.findfiles.dirtree_datafiles( path1 )
    filetable1 = datafiles.setup_filetable( tmppath, "model" )
    print "filetable1=", filetable1
    return filetable1

def get_observations(diag_type):
    obs=None
    obs_menu=ObsMenu(diag_type).obs_menu
    #path2=settings.DIAG_OBS_PATH
    #datafile2 = metrics.fileio.findfiles.dirtree_datafiles( path2)
    #obs_menu=datafile2.check_filespec()
    if type(obs_menu) is dict:
        obs=obs_menu.keys()
    return obs

def get_filetable2(obs,diag_type):
    if not os.path.exists(tmppath):
        os.makedirs(tmppath)
    obs_menu=ObsMenu(diag_type).obs_menu
    if obs_menu:
        filt2 = obs_menu[obs]
        if diag_type=='AMWG':
            path2=settings.DIAG_AMWG_OBS_PATH
        elif diag_type=='LMWG':
            path2=settings.DIAG_LMWG_OBS_PATH
        datafile2 = metrics.fileio.findfiles.dirtree_datafiles(path2,filt2)
        print "datafile2=", datafile2
        filetable2 = datafile2.setup_filetable(tmppath,"obs")
    else:
        if diag_type=='AMWG':
            path2=settings.DIAG_AMWG_OBS_PATH
        elif diag_type=='LMWG':
            path2=settings.DIAG_LMWG_OBS_PATH

        datafile2 = metrics.fileio.findfiles.dirtree_datafiles( path2)
        obs_menu=datafile2.check_filespec()
        filt2 = obs_menu[obs]
        datafile2 = metrics.fileio.findfiles.dirtree_datafiles(path2,filt2)
        filetable2 = datafile2.setup_filetable(tmppath,"obs")
    return filetable2

def get_input_parameter(package, diag_model, plot_set, seasonID, variableID,obsID):
    dg_menu=diagnostics_menu()[str(package)]()
    plot_set_obj=dg_menu.list_diagnostic_sets()[str(plot_set)]
    filetable1=get_filetable1(diag_model)
    if obsID=='':
        filetable2=None
    else:
        filetable2=get_filetable2(obsID,package)
    return plot_set_obj,filetable1,filetable2, variableID, seasonID


