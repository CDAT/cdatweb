from django.conf.urls import patterns, include, url
from django.contrib import admin

from . import views
from .apps.vtk_view import views as vtk_views

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', views.index, name='index'),
    url(r'^vtk/$', vtk_views.vtk_canvas, name='index'),
    url(r'^vtk/cone.html', vtk_views.vtk_cone)
)

# Development
from django.conf import settings
if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    media = static(settings.DATA_URL, document_root=settings.DATA_ROOT)

    urlpatterns = media + staticfiles_urlpatterns() + urlpatterns
