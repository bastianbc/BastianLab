from django.urls import path
from django.conf import settings
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static

urlpatterns = [
    path("", views.cns, name="cnses"),
    path("filter_cns", views.filter_cns, name="filter-cns"),
] + staticfiles_urlpatterns()
