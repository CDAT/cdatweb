import os, sys, errno
from django.utils import simplejson
from metrics.diagnostic_groups import *
from django.http import Http404,HttpResponse,HttpResponseRedirect
import utils
from django.shortcuts import render, get_object_or_404,render_to_response
from metrics.frontend.uvcdat import *
import json
from lib_util.plots import save_plot as save_plot

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
    dg_menu=diagnostics_menu()[diagnosticType]()
    filetable1 = utils.get_filetable1()
    obs=request.GET['plot_obs']
    filetable2=utils.get_filetable2(obs)
    #filetable2 = utils.get_filetable2()
    diagnostics_set_name=request.GET['plot_set']
    variables=dg_menu.list_variables(filetable1,filetable2,diagnostics_set_name)
    obj={'variables_list':variables}
    json_res=simplejson.dumps(obj)
    return HttpResponse(json_res, content_type="application/json")

def get_plot_aux_options(request):
    filetable1 = utils.get_filetable1()
    obs=request.GET['plot_obs']
    filetable2=utils.get_filetable2(obs)
     
    #filetable2 = utils.get_filetable2()
    diagnosticType=request.GET['plot_package']
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

def get_plot_obs(request):
    obs_list=utils.get_observations()
    obj={'observation_list':obs_list}
    json_res=simplejson.dumps(obj)
    return HttpResponse(json_res, content_type="application/json")

def run(request):
    diagnosticType=request.GET['plot_package']
    plot_set_name=request.GET['plot_set']
    seasonID=request.GET['seasonID']
    variableID=request.GET['variableID']
    obs=request.GET['plot_obs']
    filetable2=utils.get_filetable2(obs)

    sclass,filetable1,filetable2,varid,seasonid=utils.get_input_parameter(diagnosticType,plot_set_name,seasonID,variableID,obs)
    task_id=plotdata_run(sclass,filetable1,filetable2,str(varid),seasonid)
    obj={'task_id':str(task_id)}
    print obj
    json_res=simplejson.dumps(obj)
    return HttpResponse(json_res, content_type="application/json")

def get_status(request,taskID):
    status = 0
    if taskID < 0:
        status=0
    try:
        os.kill(taskID, 0)
    except OSError, e:
        return 0
    else:
        return 1
    obj={'status': status}
    json_res=simplejson.dumps(obj)
    return HttpResponse(json_res, content_type="application/json")

def load_output(request, task_id):
    f = open(os.environ['HOME'] + '/tmp/diagout/' + task_id)
    output = f.readlines()
    f.close()
    mylines = json.loads(output[0]);
    total=mylines.__len__()
    dict_list=[]
    
    output_parent_path="/export/leung25/git/uvdjango/media"
    output_path=os.path.join(output_parent_path,task_id)
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    for i in range(0,total):
        mydict={'title':'','png':''}
        title=mylines[i]['title']

        mydict['title']=title
        outfile=os.path.join(output_path,title.replace(' ', '_'))+'.png'
        jsn = json.loads(mylines[i]['vars'])[0]
        s2 = cdms2.createVariable(jsn,fromJSON=True)
        save_plot(s2,outfile)
        mydict['png']='/media'+ outfile.split('media')[1]
        dict_list.append(mydict)
        
    obj={'output_list':dict_list}
    json_res=simplejson.dumps(obj)
    return HttpResponse(json_res, content_type="application/json")


