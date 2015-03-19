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
