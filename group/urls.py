from django.urls import path
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path("", views.groups, name="groups"),
    path("new", views.new_group, name="new-group"),
    path("edit/<int:id>", views.edit_group, name="edit-group"),
    path("delete/<int:id>", views.delete_group, name="delete-group"),
    path("filter_groups", views.filter_groups, name="filter-groups"),
] + staticfiles_urlpatterns()
