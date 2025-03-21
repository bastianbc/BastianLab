from django.urls import path
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = [
    path("", views.list_files, name="list_files"),
    path("filter_files", views.filter_files, name="filter-files"),
] + staticfiles_urlpatterns()
