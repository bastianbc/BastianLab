"""test1 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/dev/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.urls import include, path, re_path
from django.contrib import admin
from django.views.static import serve
from django.views.generic.base import TemplateView
from django.views.generic import RedirectView
from django.conf.urls import url

# urlpatterns = [
# path('admin/', admin.site.urls),
# path('testpage/', TemplateView.as_view(template_name='pages/page.html')),
# path('quote/', include('quotes.urls')),
# path('', include('pages.urls')),
# ]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('lab/', include('lab.urls')),
    path('projects/', include('projects.urls')),
    path('libprep/', include('libprep.urls')),
    path('accession/', include('accession.urls')),
    path('auth/', include('authentication.urls')),
    # url(r'^favicon\.ico$',RedirectView.as_view(url='/static/bastianlab.png')),
    path('', include('home.urls')),
    path('group/', include('group.urls')),
    path('account/', include('account.urls')),
    path('blocks/', include('blocks.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# if settings.DEBUG:
#     import debug_toolbar
#     urlpatterns = [
#         path('__debug__/', include(debug_toolbar.urls)),
#         # url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT,}),
#         # For django versions before 2.0:
#         # url(r'^__debug__/', include(debug_toolbar.urls)),
#
#     ] + urlpatterns
