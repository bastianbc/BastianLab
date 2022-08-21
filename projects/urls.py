from django.urls import path
from django.conf import settings
from django.conf.urls import url
from django.views.static import serve
from . import views
from .views import ProjectList, ProjectCreate, ProjectUpdate, ProjectDelete
from .forms import ProjectForm

# app_name = 'projects'
urlpatterns = [
    path('', ProjectList.as_view(), name='projects-list'),
    path('project/add/', ProjectCreate.as_view(), name='project-add'),
    path('project/update/<pk>', ProjectUpdate.as_view(), name='project-update'),
    path('projectlist/<pk>/', ProjectUpdate.as_view(), name='project-update'),
    path('project/delete/<pk>', ProjectDelete.as_view(), name='project-delete')
]
