import os

from esgf_auth_backend.myproxy_logon import myproxy_logon, GetException

from django.conf import settings
from django.contrib.auth import authenticate, login
from django.http import Http404, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404, redirect, render
from django.template import Context, loader, RequestContext

def show_login(request):
    """
    Function to show the login page.
    """
    # for POST requests, attempt logging-in
    if request.POST:
        user = authenticate(username = request.POST.get('username', None),
                            password = request.POST.get('password', None),peernode=request.POST.get('peernode', None))
        if user is not None:
            if user.is_active:
                # login was successful
                login(request, user)
                return redirect(request.POST.get('redir', ''))
            else:
                return render_to_response('login_form.html', {
                    'redir': request.POST.get('redir', '..'),
                    'error_message': 'Account disabled. If you believe this is \
                                      an error, please contact an administrator.',
            }, context_instance = RequestContext(request))
                                                        
        else:
            return render_to_response('login_form.html', {
                    'redir': request.POST.get('redir', '..'),
                    'error_message': 'Username or password incorrect.',
            }, context_instance = RequestContext(request))
            
    # for GET requests, render the login page
    else:
        return render_to_response('login_form.html', {
                    'redir': request.GET.get('redir', '..')
                }, context_instance = RequestContext(request))
