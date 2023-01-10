from django.urls import path
from django.conf import settings
from django.conf.urls import url
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static

urlpatterns = [
    path("", views.sequencinglibs, name="sequencinglibs"),
    path("filter_sequencinglibs", views.filter_sequencinglibs, name="filter-sequencinglibs"),
    path("edit_sequencinglib_async", views.edit_sequencinglib_async, name="edit-sequencinglib-async"),
    path('new', views.new_sequencinglib, name='new-sequencinglib'),
    path('new_async', views.new_sequencinglib_async, name='new-sequencinglib-async'),
    path('edit/<str:id>', views.edit_sequencinglib, name='edit-sequencinglib'),
    path('delete/<str:id>', views.delete_sequencinglib, name='delete-sequencinglib'),
    path('batch_delete', views.delete_batch_sequencinglibs, name='delete-batch-sequencinglibs'),
    path('<int:id>/used_capturedlibs', views.get_used_capturedlibs, name='get-used-capturedlibs'),
    path('<int:id>/make_sequencinglib_async', views.make_sequencinglib_async, name='make_sequencinglib_async'),
    path('get_sequencinglib_async/<int:id>', views.get_sequencinglib_async, name="get-sequencinglib-async"),
    path('recreate_sequencinglib_async', views.recreate_sequencinglib_async, name="recreate-sequencinglib-async"),
    path('create_ilab_sheet', views.create_ilab_sheet, name="create-ilab-sheet"),
    path('check_can_deleted_async', views.check_can_deleted_async, name='check-can-deleted-async'),
] + staticfiles_urlpatterns()
