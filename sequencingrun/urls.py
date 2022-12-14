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
] + staticfiles_urlpatterns()
