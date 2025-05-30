from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path, re_path
from django.contrib import admin
from django.views.static import serve
from django.views.generic.base import TemplateView
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('lab/', include('lab.urls')),
    path('projects/', include('projects.urls')),
    path('libprep/', include('libprep.urls')),
    path('auth/', include('authentication.urls')),
    path('', include('home.urls')),
    path('group/', include('group.urls')),
    path('account/', include('account.urls')),
    path('blocks/', include('blocks.urls')),
    path('areas/', include('areas.urls')),
    path('method/', include('method.urls')),
    path('samplelib/', include('samplelib.urls')),
    path('capturedlib/', include('capturedlib.urls')),
    path('sequencinglib/', include('sequencinglib.urls')),
    path('sequencingrun/', include('sequencingrun.urls')),
    path('buffer/', include('buffer.urls')),
    path('areatype/', include('areatype.urls')),
    path('bait/', include('bait.urls')),
    path('body/', include('body.urls')),
    path('barcodeset/', include('barcodeset.urls')),
    path('migration/', include('migration.urls')),
    path('sequencingfile/', include('sequencingfile.urls')),
    path('variant/', include('variant.urls')),
    path('gene/', include('gene.urls')),
    path('sheet/', include('sheet.urls')),
    path('wiki/', include('wiki.urls')),
    path('analysisrun/', include('analysisrun.urls')),
    path('cns/', include('cns.urls')),
    path('qc/', include('qc.urls')),
    path('notification/', include('notification.urls')),
    path('file_manager/', include('file_manager.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = "core.views.error_404"
handler403 = "core.views.error_403"
handler500 = "core.views.error_500"
