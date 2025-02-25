from django.urls import path
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path("", views.areas, name="areas"),
    path("filter_areas", views.filter_areas, name="filter-areas"),
    path('new', views.new_area, name='new-area'),
    path('add_area_to_block_async', views.add_area_to_block_async, name='add-area-to-block-async'),
    path('edit/<str:id>', views.edit_area, name='edit-area'),
    path("edit_area_async", views.edit_area_async, name="edit-area-async"),
    path('delete/<str:id>', views.delete_area, name='delete-area'),
    path('batch_delete', views.delete_batch_areas, name='delete-batch-areas'),
    path('check_can_deleted_async', views.check_can_deleted_async, name='check-can-deleted-async'),
    path("get_collections", views.get_collections, name='get-collections'),
    path("get_area_types", views.get_area_types, name='get-area-types'),
    path("get_area_vaiants", views.get_area_vaiants, name='get_area_vaiants'),
] + staticfiles_urlpatterns()
