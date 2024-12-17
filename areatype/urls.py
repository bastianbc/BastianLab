from django.urls import path
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path("", views.areatypes, name="areatypes"),
    path("new", views.new_areatype, name="new-areatype"),
    path("edit/<int:id>", views.edit_areatype, name="edit-areatype"),
    path("delete/<int:id>", views.delete_areatype, name="delete-areatype"),
    path("filter_areatypes", views.filter_areatype, name="filter-areatype"),
   
] + staticfiles_urlpatterns()
