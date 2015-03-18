from django.shortcuts import render
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
import os

def index(request):
    return render(request, 'nav.html', {})

def search(request):
    context = RequestContext(request)
    if request.method == 'POST':
        context = request.POST.dict()
        host = context["host"]
        query = {}
        if context['text']:
            print context['text']
            query['query'] = context['text']
        if context['project']:
            print 'text'
            query['project'] = context['project']
        if context['limit']:
            print 'limit'
            query['limit'] = context['limit']
        if context['offset']:
            print 'offset'
            query['offset'] = context['offset']
        query['fields'] = 'size,timestamp,project,id,experiment,title,url'
        print query
        data = files(host, query)
    else:
        data = "none"
    return render(request, 'cdat_fe/search.html', {"data":data})
