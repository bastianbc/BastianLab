from django.urls import path
from django.conf import settings
from django.conf.urls import url
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static

urlpatterns = [
    path("", views.nucacids, name="nucacids"),
    path("filter_nucacids", views.filter_nucacids, name="filter-nucacids"),
    path("edit_nucacid_async", views.edit_nucacid_async, name="edit-nucacid-async"),
    path('new', views.new_nucacid, name='new-nucacid'),
    path('new_async', views.new_nucacid_async, name='new-nucacid-async'),
    path('edit/<str:id>', views.edit_nucacid, name='edit-nucacid'),
    path('delete/<str:id>', views.delete_nucacid, name='delete-nucacid'),
] + staticfiles_urlpatterns()
