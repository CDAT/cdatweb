from django.conf.urls import patterns, include, url
from django.views.generic import DetailView, ListView
from django.conf import settings
from login import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = patterns('login.views',
        # /
        url(r'^/?$', 'show_login', name='login'),
)
urlpatterns += staticfiles_urlpatterns()
