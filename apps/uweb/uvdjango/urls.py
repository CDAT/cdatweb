from django.conf.urls import patterns, include, url
from django.conf import settings
if not settings.configured:
    settings.configure()

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
                       url("",include('django_socketio.urls')),
                       (r'^media/(?P<path>.*)$','django.views.static.serve',
                                    {'document_root': settings.MEDIA_ROOT}),
                       (r'', include('home.urls')),
                       (r'^plots/', include('home.urls')),
                       (r'^login/', include('login.urls', namespace='login')),
    # Examples:
    # url(r'^$', 'uvdjango.views.home', name='home'),
    # url(r'^uvdjango/', include('uvdjango.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
