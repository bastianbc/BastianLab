from django.urls import path
from django.conf import settings

from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static

urlpatterns = [
    path("", views.sequencingfiles, name="sequencingfiles"),
    path("filter_sequencingfiles", views.filter_sequencingfiles, name="filter-sequencingfiles"),
    path('new', views.new_sequencingfile, name='new-sequencingfile'),
    path('edit/<str:id>', views.edit_sequencingfile, name='edit-sequencingfile'),
    path('delete/<str:id>', views.delete_sequencingfile, name='delete-sequencingfile'),
    path('batch_delete', views.delete_batch_sequencingfiles, name='delete-batch-sequencingfiles'),
    path('check_can_deleted_async', views.check_can_deleted_async, name='checkcan-deleted-async'),

    path("sequencingfilesets", views.sequencingfilesets, name="sequencingfilesets"),
    path("filter_sequencingfilesets", views.filter_sequencingfilesets, name="filter-sequencingfilesets"),
    path('sequencingfileset/new', views.new_sequencingfileset, name='new-sequencingfileset'),
    path('sequencingfileset/edit/<str:id>', views.edit_sequencingfileset, name='edit-sequencingfileset'),
    path('sequencingfileset/delete/<str:id>', views.delete_sequencingfileset, name='delete-sequencingfileset'),
    path('sequencingfileset/batch_delete', views.delete_batch_sequencingfilesets, name='delete-batch-sequencingfilesets'),
    path('check_can_deleted_async_set', views.check_can_deleted_async_set, name='checkcan-deleted-async-set'),

    path('tempfiles', views.tempfiles, name='tempfiles'),
    path('filter_temp_directory', views.filter_temp_directory, name='filter_temp_directory'),
] + staticfiles_urlpatterns()
