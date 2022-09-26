from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.urls import include, path, re_path
from django.contrib import admin
from django.views.static import serve
from django.views.generic.base import TemplateView
from django.views.generic import RedirectView
from django.conf.urls import url

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
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = "core.views.error_404"
handler403 = "core.views.error_403"
handler500 = "core.views.error_500"
