from django.urls import path
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path("", views.projects, name="projects"),
    path("filter_projects", views.filter_projects, name="filter-projects"),
    path('new', views.new_project, name='new-project'),
    path('edit/<str:id>', views.edit_project, name='edit-project'),
    path("edit_project_async", views.edit_project_async, name="edit-project-async"),
    path('delete/<str:id>', views.delete_project, name='delete-project'),
    path('get_pi_options', views.get_pi_options, name='get-pi-options'),
] + staticfiles_urlpatterns()
