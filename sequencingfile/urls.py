from django.urls import path
from django.conf import settings
from django.conf.urls import url
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static

urlpatterns = [
    path("", views.sequencingfiles, name="sequencingfiles"),
    path("filter_sequencingfiles", views.filter_sequencingfiles, name="filter-sequencingfiles"),
] + staticfiles_urlpatterns()
