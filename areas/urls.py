from django.urls import path
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path("", views.areas, name="areas"),
    path("filter_areas", views.filter_areas, name="filter-areas"),
    path('new', views.new_area, name='new-area'),
    path('new_async', views.new_area_async, name='new-area-async'),
    path('edit/<str:id>', views.edit_area, name='edit-area'),
    path("edit_area_async", views.edit_area_async, name="edit-area-async"),
    path('delete/<str:id>', views.delete_area, name='delete-area'),
] + staticfiles_urlpatterns()
