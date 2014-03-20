import fcntl
import os
#import pycurl
from urllib import urlencode
import lib_util as util

from lib_util.plots import boxfill as box_fill
from lib_util.plots import getVar as get_var
from lib_util.file_handler import download_file as download_file
from lib_util.calculator import eval_cdat_cmd as eval_cdat
from lib_util.esgf_connector import datasetId_to_html_list as datasetId2htmllist
#from util.esgf import *

#import proof_of_concept

from esgf_auth_backend.query import query as esgf_query
from esgf_auth_backend.query import get_data_node_list as esgf_data_node_list


from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404,render_to_response
from django.template import Context, loader, RequestContext
from django.conf import settings
from django.utils import simplejson
from django.core.servers.basehttp import FileWrapper
if not settings.configured:
    settings.configure()

import tempfile,zipfile
import vcs


def diag_batch(request):
    #image_dir=request.POST['directory']
    return render(request, "diag_carousel.html")

def esgf_data_node(request):
    host=settings.ESGF_HOST 
    data_node_list=esgf_data_node_list(host)
    obj={'res':data_node_list}
    json_res=simplejson.dumps(obj)
    return HttpResponse(json_res, content_type="application/json")

def esgf_search(request):
    search_str=request.GET['search_str']
    obj={"res":esgf_query("pcmdi9.llnl.gov",search_str)}
    #obj={"res":[{"fileID":"fileID1","url":"url1"},{"fileID":"fileID2","url":"url2"}]}
    json_res=simplejson.dumps(obj)
    return HttpResponse(json_res, content_type="application/json")

def diag_home(request):
    #image_dir=request.POST['directory']
    if not request.user.is_authenticated():
        # send them to the login page, with a ?redir= on the end pointing back to this page
        return HttpResponseRedirect(reverse('login:login') + "?" + urlencode({'redir':reverse('home.views.diag_home')}))
    else:
        host=settings.ESGF_HOST 
        data_node_list=esgf_data_node_list(host)
        mycontent={'data_node_list':data_node_list,'uvis_hostname':settings.UVIS_HOSTNAME, "user":request.user.username}
        return render(request, "home.html",mycontent)
    """
    host=settings.ESGF_HOST 
    data_node_list=esgf_data_node_list(host)
    mycontent={'data_node_list':data_node_list,'uvis_hostname':settings.UVIS_HOSTNAME, "user":'williams13'}
    """

def testing(request):
    return render(request, "test.html")


def downloadFile(request):
    if not request.user.is_authenticated():
        # send them to the login page, with a ?redir= on the end pointing back to this page
        return HttpResponseRedirect(reverse('login:login') + "?" + urlencode({'redir':reverse('home.views.make_main_window')}))
    else:
        active_cert = settings.PROXY_CERT_DIR + request.user.username+'/'+request.user.username + '.pem'
        myfile=request.GET['fnm']
        myvar=request.GET['varlist[]']
        outfile=download_file(myfile,myvar,active_cert)
        """
        temp = tempfile.TemporaryFile()
        archive = zipfile.ZipFile(temp, 'w', zipfile.ZIP_DEFLATED)
        archive.write(outfile, 'file.txt')
        archive.close()
        """
        wrapper=FileWrapper(file(outfile))
        response = HttpResponse(wrapper, content_type="application/x-netcdf")
        response['Content-Disposition']='attachment; filename=%s'%outfile
        response['Content-Length']=os.path.getsize(outfile)
        #temp.seek(0)

        return response

def calculate(request):
    cdat_cmd=request.GET['cmd']
    myvar=request.GET['myvar']
    mynewvar=request.GET['mynewvar']
    myfile=request.GET['myfile']
    my_new_var=eval_cdat(cdat_cmd,myfile,myvar,mynewvar)
    obj={"outfile":my_new_var,"myfileid":500}
    json_res=simplejson.dumps(obj) 
    return HttpResponse(json_res, content_type="application/json")

def logout_view(request):
    try:
        logout(request)
    except Exception as e:
        #user has not been logged in.
        #redir to login page
        return HttpResponseRedirect(reverse('login:login'))
        
    return render_to_response('logout.html')


def show_index(request):
    return render(request, 'testplot_form.html', { })

def boxfill(request):
    if not request.user.is_authenticated():
        # send them to the login page, with a ?redir= on the end pointing back to this page
        return HttpResponseRedirect(reverse('login:login') + "?" + urlencode({'redir':reverse('home.views.boxfill')}))
    else:
        if request.GET:
            return render(request, 'boxfill_form.html', { })
        else:
            
            try:
                myfile=request.POST['file']
                myvar=request.POST['var']
                latitude_from=int(request.POST['latitude_from'])
                latitude_to=int(request.POST['latitude_to'])
                longitude_from=int(request.POST['longitude_from'])
                longitude_to=int(request.POST['longitude_to'])
                time_slice_from=int(request.POST['time_slice_from'])
                time_slice_to=int(request.POST['time_slice_to'])
                lev1=None
                lev2=None
                if 'lev1' in request.POST:
                    lev1=request.POST['lev1']
                if 'lev2' in request.POST:
                    lev2=request.POST['lev2']
            except:
                return render(request, 'boxfill_form.html', {
                    'error_message': "Please fill all required fields",
                })
        
            selection_dict = {
                'latitude':(latitude_from,latitude_to),
                'longitude':(longitude_from,longitude_to),
                'time':slice(time_slice_from,time_slice_to)
            }
               
            # tell curl what certificate to use
            #TODO: sanitize request.user.name!
            active_cert = settings.PROXY_CERT_DIR + request.user.username + '.pem'
            plot_filename = box_fill(myfile, myvar, selection_dict, proxy_cert = active_cert)
            
            if not plot_filename:
                return render_to_response("accessDenied.html",None,context_instance=RequestContext(request))
            
            return render(request, 'boxfill.html', {
                'png': plot_filename,
            })
    
def make_boxfill(request):
    if not request.user.is_authenticated():
        # send them to the login page, with a ?redir= on the end pointing back to this page
        return HttpResponseRedirect(reverse('login:login') + "?" + urlencode({'redir':reverse('home.views.main_main_window')}))
    else:
        active_cert = settings.PROXY_CERT_DIR + request.user.username + '.pem'
        myfile=request.GET['fnm']
        myvar=request.GET['var']
        n=request.GET['n']
        s=request.GET['s']
        e=request.GET['e']
        w=request.GET['w']
        selection_dict = {'latitude':(int(n),int(s)),'longitude':(int(e),int(w)),'time':slice(0,1)}
        try:
            plot_filename = box_fill(myfile, myvar, selection_dict, proxy_cert = active_cert)
            obj={"png":plot_filename}
            json_res=simplejson.dumps(obj) 
        except Exception, err:
            obj={"png":""}
            json_res=simplejson.dumps(obj) 
        return HttpResponse(json_res, content_type="application/json")

def get_variable(request):
    myfile=request.GET['file']
    varlist=get_var(myfile)
    obj={"variable":varlist}
    json_res=simplejson.dumps(obj) 
    return HttpResponse(json_res, content_type="application/json")


def make_main_window(request,json_param=None):
    if not request.user.is_authenticated():
        # send them to the login page, with a ?redir= on the end pointing back to this page
        return HttpResponseRedirect(reverse('login:login') + "?" + urlencode({'redir':reverse('home.views.make_main_window')}))
    else:
        #if request.GET:
           #return render(request, 'testplot_form.html', { })
        #else:
            #if not json_param:
            #    print "testing through form (no link from ESGF yet)"
            n="-90"
            s="90"
            e="0"
            w="180"

            try:
                #myfile=request.POST['file']
                lev1=None
                lev2=None
                if 'lev1' in request.POST:
                    lev1=request.POST['lev1']
                if 'lev2' in request.POST:
                    lev2=request.POST['lev2']
            except:

                return render(request, 'testplot_form.html', {
                    'error_message': "Please fill all required fields",
                })
        
            selection_dict = {
                'latitude':(-90,90),
                'longitude':(0,180),
                'time':slice(0,1)
            }
            myfile = "http://pcmdi9.llnl.gov/thredds/dodsC/cmip5.output1.INM.inmcm4.1pctCO2.mon.atmos.Amon.r1i1p1.cl.20130207.aggregation.1"
            # tell curl what certificate to use
            #TODO: sanitize request.user.name!
            active_cert = settings.PROXY_CERT_DIR + request.user.username + '.pem'
            varlist=get_var(myfile)
            if not varlist:
                return render_to_response("accessDenied.html",None,context_instance=RequestContext(request))

            """
            if json_param:
                plot_filename = box_fill(myfile, varlist, selection_dict, proxy_cert = active_cert)
            else:
                plot_filename=None
            """
            #plot_filename=settings.MEDIA_URL + "plot-boxfill_httppcmdi9llnlgovthreddsdodsccmip5output1inminmcm41pctco2monatmosamonr1i1p1ccb20130207aggregation1_ccb_latitude_-90_90_longitude_-180_180_time_slice1_6_none_none_none.png"
            """
            mycontent={"curOpt":{"total":total_plot,"type":plot_type,"n":n,"s":s,"e":e,"w":w,"active_plot":active_plot},
                    "dataset":[{"file":myfile,"var":varlist,"id":"2"}],"user":request.user.username,
                    }
            """
            mycontent={"dataset":[{"file":myfile,"var":varlist,"id":"2"}],"user":request.user.username}
            return render(request, 'plot.html',mycontent)

def make_datasetId_form(request):
    return render(request, 'test_datasetId_form.html', { })


def run_main_window(request):
    if not request.user.is_authenticated():
        print "NOT AUTHENTICATED"
        # send them to the login page, with a ?redir= on the end pointing back to this page
        return HttpResponseRedirect(reverse('login:login') + "?" + urlencode({'redir':reverse('home.views.run_main_window')}))
    else:
        if request.GET:
            return render(request, 'test_datasetId_form.html', { })
        else:
            datasetIds=request.POST['datasetIds']
            n="-90"
            s="90"
            e="0"
            w="180"
            counter = 1 
            mylist_dict=[]
            try:
                datasetIds_token=datasetIds.split(',')
                for datasetId in datasetIds_token:
                    print datasetId
                    htmllist=datasetId2htmllist(datasetId)
                    myhtmllist=htmllist.split(',')
                    for html in myhtmllist:
                        myfile=html
                        print html
                        active_cert = settings.PROXY_CERT_DIR + request.user.username + '.pem'
                        varlist=get_var(myfile)
                        if not varlist:
                            return render_to_response("accessDenied.html",None,context_instance=RequestContext(request))
                        mydict={"file":myfile,"var":varlist,"id":counter}
                        mylist_dict.append(mydict)
                        counter=counter+1
                print mylist_dict
            except Exception, err:
                print err
                return render(request, 'test_datasetId_form.html', {
                    'error_message': "Please fill all required fields",
                    })
        
            selection_dict = {
                'latitude':(-90,90),
                'longitude':(0,180),
                'time':slice(0,1)
            }
               
            mycontent={"dataset":mylist_dict,"user":request.user.username}
            return render(request, 'plot.html',mycontent)
