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
    path('<int:id>/update_async', views.update_async, name='update_async'),
] + staticfiles_urlpatterns()
