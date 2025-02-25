from django.urls import path
from django.conf import settings

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
    path('batch_delete', views.delete_batch_nucacids, name='delete-batch-nucacids'),
    path("get_na_types", views.get_na_types, name="get-na-types"),
    path('check_can_deleted_async', views.check_can_deleted_async, name='check-can-deleted-async'),
] + staticfiles_urlpatterns()
