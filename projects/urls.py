from django.urls import path
from django.conf import settings
from django.conf.urls import url
from django.views.static import serve
from . import views
from .views import ProjectList, ProjectCreate, ProjectUpdate, ProjectDelete
from .forms import ProjectForm
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static

# app_name = 'projects'
urlpatterns = [
    # path('', ProjectList.as_view(), name='projects-list'),
    # path('project/add/', ProjectCreate.as_view(), name='project-add'),
    # path('project/update/<pk>', ProjectUpdate.as_view(), name='project-update'),
    # path('projectlist/<pk>/', ProjectUpdate.as_view(), name='project-update'),
    # path('project/delete/<pk>', ProjectDelete.as_view(), name='project-delete'),
    path("", views.projects, name="projects"),
    path("filter_projects", views.filter_projects, name="filter-projects"),
    path('new', views.new_project, name='new-project'),
    path('edit/<str:id>', views.edit_project, name='edit-project'),
    path('delete/<str:id>', views.delete_project, name='delete-project'),
] + staticfiles_urlpatterns()
