import json
import vtk_launcher
from django.shortcuts import render
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from search import files

_browser_help = (
    "Choose a variable from the list of files available on the server "
    "and drag it to the canvas."
)


def _refresh(request):
    """Refresh the visualization session information."""
    # check the session for a vtkweb instance
    vis = request.session.get('vtkweb')

    if vis is None or vtk_launcher.status(vis.get('id', '')) is None:
        # open a visualization instance
        vis = vtk_launcher.new_instance()
        request.session['vtkweb'] = vis

    return dict(vis)


def vtk_viewer(request):
    """Open the main visualizer view."""
    try:
        data = _refresh(request)
    except Exception:
        data = {}
    data['main'] = 'main'
    data['error'] = 'error'
    data['search'] = {
        'help': ''
    }
    options = {
        'resizable': True
    }
    data['options'] = mark_safe(json.dumps(options))
    return render(
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
        # query['fields'] = 'size,timestamp,project,id,experiment,title,url'

        try:
            results['data'] = files(host, query)
        except Exception:
            results['data'] = "failed to reach node"
            print "failed to reach node"
    except Exception:
        results['data'] = "failed to parse json"
        print "failed to parse json"

    return HttpResponse(json.dumps(results))
