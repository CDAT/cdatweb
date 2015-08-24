from django.conf.urls import patterns, include, url

from .apps.vtk_view import views as vtk_views

urlpatterns = patterns(
    '',
    url(r'^$', vtk_views.vtk_viewer),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^vtk/search', vtk_views.search),
    url(r'^vtk/launch', vtk_views.vtkweb_launcher)
)

# Development
from django.conf import settings  # noqa
if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    media = static(settings.DATA_URL, document_root=settings.DATA_ROOT)

    urlpatterns = media + staticfiles_urlpatterns() + urlpatterns
