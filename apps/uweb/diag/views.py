import os, sys, errno
from django.utils import simplejson
from metrics.diagnostic_groups import *
from django.http import Http404,HttpResponse,HttpResponseRedirect
import utils
from django.shortcuts import render, get_object_or_404,render_to_response
from metrics.frontend.uvcdat import *
import json
from lib_util.plots import save_plot as save_plot
from django.conf import settings
import time
import xml.etree.ElementTree as ET
import cdms2

def get_plot_package(request):
    packageList=diagnostics_menu().keys()
    obj={'package_list':packageList}
    json_res=simplejson.dumps(obj)
    return HttpResponse(json_res, content_type="application/json")


def get_plot_set(request):
    diagnosticType=request.GET['plot_package']
    dg_menu=diagnostics_menu()[str(diagnosticType)]()
    sm=dg_menu.list_diagnostic_sets()
    obj={'plot_set':sm.keys()}
    json_res=simplejson.dumps(obj)
    return HttpResponse(json_res, content_type="application/json")

def get_plot_seasons(request):
    diagnosticType=request.GET['plot_package']
    dg_menu=diagnostics_menu()[str(diagnosticType)]()
    seasons=dg_menu.list_seasons()
    obj={'season_list':seasons}
    json_res=simplejson.dumps(obj)
    return HttpResponse(json_res, content_type="application/json")

def get_plot_variable(request):
    diagnosticType=request.GET['plot_package']
    modelType=request.GET['plot_model']
    dg_menu=diagnostics_menu()[diagnosticType]()
    filetable1 = utils.get_filetable1(modelType)
    obs=request.GET['plot_obs']
    if obs=='':
        filetable2=None
    else:
        filetable2=utils.get_filetable2(obs,diagnosticType)
    #filetable2 = utils.get_filetable2()
    diagnostics_set_name=request.GET['plot_set']
    variables=dg_menu.list_variables(filetable1,filetable2,diagnostics_set_name)
    obj={'variables_list':variables}
    json_res=simplejson.dumps(obj)
    return HttpResponse(json_res, content_type="application/json")

def get_plot_aux_options(request):
    diagnosticType=request.GET['plot_package']
    modelType=request.GET['plot_model']
    filetable1 = utils.get_filetable1(modelType)
    obs=request.GET['plot_obs']
    if obs=='':
        filetable2=None
    else:
        filetable2=utils.get_filetable2(obs,diagnosticType)
    #filetable2 = utils.get_filetable2()
    diagnostics_set_name=request.GET['plot_set']
    dg_menu=diagnostics_menu()[diagnosticType]()
    varmenu=dg_menu.all_variables(filetable1,filetable2,diagnostics_set_name)
    varname=request.GET['plot_variable']
    if varname in varmenu.keys():
	variable=varmenu[varname](varname,diagnostics_set_name,dg_menu)
	auxList=variable.varoptions()
    else:
	auxList = None
    obj = {'aux_list':auxList}
    json_res = simplejson.dumps(obj)
    return HttpResponse(json_res, content_type="application/json")

def get_plot_models(request):
    diagnosticType=request.GET['plot_package']
    models_list=[]
    if diagnosticType=='AMWG':
        models_list.append(['CAM_HIRES','CAM_HIRES'])
        models_list.append(['CAM_LORES','CAM_LORES'])
        models_list.append(['CAM_OUTPUT','CAM_OUTPUT'])
    elif diagnosticType=='LMWG':
        models_list.append(['CLM_HIRES','CLM_HIRES'])
        models_list.append(['CLM_LORES','CLM_LORES'])
        models_list.append(['CLM_OUTPUT','CLM_OUTPUT'])

    obj={'models_list':models_list}
    json_res=simplejson.dumps(obj)
    return HttpResponse(json_res, content_type="application/json")

def get_plot_obs(request):
    diagnosticType=request.GET['plot_package']
    obs_list=utils.get_observations(diagnosticType)
    obj={'observation_list':obs_list}
    json_res=simplejson.dumps(obj)
    return HttpResponse(json_res, content_type="application/json")

def run_elo(request):
    diagnosticType=request.GET['plot_package']
    modelType=request.GET['plot_model']
    plot_set_name=request.GET['plot_set']
    seasonID=request.GET['seasonID']
    variableID=request.GET['variableID']
    obs=request.GET['plot_obs']
    if obs=='':
        filetable2=None
    else:
        filetable2=utils.get_filetable2(obs,diagnosticType)

    sclass,filetable1,filetable2,varid,seasonid=utils.get_input_parameter(diagnosticType,modelType,plot_set_name,seasonID,variableID,obs)
    outputPath=settings.DIAG_MEDIA
    taskID = str(time.time()) # TODO: this taskID should be a unique identifier.
    output_parent_path=settings.DIAG_MEDIA
    output_path=os.path.join(output_parent_path,taskID)
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    p_object=plotdata_run(sclass,filetable1,filetable2,str(varid),seasonid, outputPath, taskID)
    pid = p_object.pid
    obj={'task_id':str(pid)}
    task_tracker=utils.TaskTracker()
    task_tracker.add_task(pid,p_object)
    json_res=simplejson.dumps(obj)
    
    return HttpResponse(json_res, content_type="application/json")

def get_status(request,taskID):
    task_id=int(taskID)
    p_object=utils.TaskTracker().get_task(task_id)
    status=plotdata_status(p_object)
    status1 = 1
    if taskID < 0:
        status1=1
    try:
        os.kill(task_id, 0)
        status1=0
    except OSError, e:
        status1=1
        pass
    print "STATUS : ", status, ", ", status1
    obj={'status': status}
    json_res=simplejson.dumps(obj)
    return HttpResponse(json_res, content_type="application/json")

def load_output(request, taskID):
    diagnosticType=request.GET['plot_package']
    #if diagnosticType=='AMWG':
    #    taskID='AMWG'
    #else:
    #    taskID='LMWG'
    task_id=int(taskID)
    p_object=utils.TaskTracker().get_task(task_id)
    if p_object:
        outfile = plotdata_results(p_object)
    #task_id=int(taskID)
    #outfile=utils.TaskTracker().get_task(task_id)
    #look for the output file that ends in diagoutput
    #outfile=os.path.join(settings.DIAG_MEDIA,taskID)
    filelist=os.listdir(outfile)
    outfilename=None
    for filename in filelist:
        if filename.endswith('.xml'):
            outfilename=filename
            break
    mylist=[]

    tree = ET.parse(os.path.join(outfile,outfilename))
    root=tree.getroot()
    elementlist=root.findall('ncfile')
    for element in elementlist:
        full_filepath=os.path.join(outfile,element.text)
        f=cdms2.open(full_filepath)
        varlist=f.plot_these
        plot_type=f.presentation
        mylist.append({'varlist':varlist,'plot_type':plot_type,'fullpath':os.path.join(outfile,element.text),'filename':element.text})

    """
    f = open(os.path.join(outfile,outfilename))
    #f = open("/export/leung25/uvis/apps/uweb/media/diag/1/1389223541.14.diagoutput")
    output = f.readlines()
    f.close()
    total=len(output)
    
    dict_list=[] 
    output_parent_path=settings.DIAG_MEDIA
    output_path=os.path.join(output_parent_path,taskID)
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    for i in range(0,total):
        mydict={'title':'','png':''}
        myline=json.loads(output[i])
        title=myline['title']
        mydict['title']=title
        outfile=os.path.join(output_path,title.replace(' ', '_'))+'.png'

        jsn = json.loads(myline['vars'])[0]
        s2 = cdms2.createVariable(jsn,fromJSON=True)
        #save_plot(s2,outfile)
        print 'init vcs'
        x = vcs.init()
        print 'plotting'
        x.plot(s2,bg=1)
        print 'pnging'
        x.png(outfile)
        print 'retuirning'
        mydict['png']='/media'+ outfile.split('media')[1]
        dict_list.append(mydict)
    """    
    obj={'output_list':mylist}
    json_res=simplejson.dumps(obj)
    return HttpResponse(json_res, content_type="application/json")
