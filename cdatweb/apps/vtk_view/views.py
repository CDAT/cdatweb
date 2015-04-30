import json
import vtk_launcher
import os
from django.shortcuts import render
from django.utils.safestring import mark_safe
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext, loader
from django.forms.models import model_to_dict
from django.forms.util import ErrorList
from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_exempt
from django.core.files import File
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from search import files

_browser_help = '''
Choose a variable from the list of files available on the server and drag it to the canvas.
'''.strip()


def _refresh(request):
    '''
    Refresh the visualization session information.
    '''
    # check the session for a vtkweb instance
    vis = request.session.get('vtkweb')

    if vis is None or vtk_launcher.status(vis.get('id', '')) is None:
        # open a visualization instance
        vis = vtk_launcher.new_instance()
        request.session['vtkweb'] = vis

    return dict(vis)


def vtk_viewer(request):
    '''
    Open the main visualizer view.
    '''
    try:
        data = _refresh(request)
    except Exception:
        data = {}
    data['main'] = 'browser'
    data['browser'] = {
        'help': _browser_help
    }
    options = {
        'resizable': True
    }
    data['options'] = mark_safe(json.dumps(options))
    return  render(
        request,
        'vtk_view/cdat_viewer.html',
        data
    )


def vtk_test(request, test="cone"):
    return render(request, 'vtk_view/view_test.html', {"test": test})

@csrf_exempt
def search(request):
    try:
        results = {}
        inputstring = request.POST.get('query')
        context = json.loads(inputstring)
    
        host = context["host"]
        print host
        query = {}
        if context["text"]:
            query["query"] = context["text"]
        if context["project"]:
            query["project"] = context["project"]
        if context["limit"]:
            query["limit"] = context["limit"]
        if context["offset"]:
            query["offset"] = context["offset"]
        #query['fields'] = 'size,timestamp,project,id,experiment,title,url'
        
        try:
            results['data'] = files(host, query)
        except Exception,e:
            results['data'] = "failed to reach node"
            print "failed to reach node"
    except Exception,e:
        results['data'] = "failed to parse json"
        print "failed to parse json"

    print "DONE"
    return HttpResponse(json.dumps(results))

