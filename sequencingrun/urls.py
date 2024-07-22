from django.urls import path
from django.conf import settings
from django.conf.urls import url
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static

urlpatterns = [
    path("", views.sequencingruns, name="sequencingruns"),
    path("filter_sequencingruns", views.filter_sequencingruns, name="filter-sequencingruns"),
    path("edit_sequencingrun_async", views.edit_sequencingrun_async, name="edit-sequencingrun-async"),
    path('new', views.new_sequencingrun, name='new-sequencingrun'),
    path('new_async', views.new_sequencingrun_async, name='new-sequencingrun-async'),
    path('edit/<str:id>', views.edit_sequencingrun, name='edit-sequencingrun'),
    path('delete/<str:id>', views.delete_sequencingrun, name='delete-sequencingrun'),
    path('batch_delete', views.delete_batch_sequencingruns, name='delete-batch-sequencingruns'),
    path('<int:id>/used_sequencinglibs', views.get_used_sequencinglibs, name='get-used-sequencinglibs'),
    path('check_can_deleted_async', views.check_can_deleted_async, name='check-can-deleted-async'),
    path('get_facilities', views.get_facilities, name='get-facilities'),
    path('get_sequencers', views.get_sequencers, name='get-sequencers'),
    path('get_pes', views.get_pes, name='get-pes'),
    path('add_async', views.add_async, name="add_async"),
    path('<int:id>/get_sequencing_files', views.get_sequencing_files, name="get-sequencing-files"),
    path('<int:id>/save_sequencing_files', views.save_sequencing_files, name="save-sequencing-files"),
    path('get_sample_libs_async', views.get_sample_libs_async, name='get-sample-libs-async'),
    path('save_analysis_run', views.save_analysis_run, name='save-analysis-run'),
] + staticfiles_urlpatterns()
