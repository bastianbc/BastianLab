from django.urls import path
from django.conf import settings
from django.conf.urls import url
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static

urlpatterns = [
    path("", views.samplelibs, name="samplelibs"),
    path("filter_samplelibs", views.filter_samplelibs, name="filter-samplelibs"),
    path("edit_samplelib_async", views.edit_samplelib_async, name="edit-samplelib-async"),
    path('new', views.new_samplelib, name='new-samplelib'),
    path('new_async', views.new_samplelib_async, name='new-samplelib-async'),
    path('edit/<str:id>', views.edit_samplelib, name='edit-samplelib'),
    path('delete/<str:id>', views.delete_samplelib, name='delete-samplelib'),
    path('batch_delete', views.delete_batch_samplelibs, name='delete-batch-samplelibs'),
    path('<int:id>/used_nucacids', views.get_used_nucacids, name='get-used-nucacids'),
    path('update_async', views.update_sl_na_link_async, name="update-async"),
    path('print_as_csv', views.print_as_csv, name="print_as_csv"),
    path('check_can_deleted_async', views.check_can_deleted_async, name='checkcan-deleted-async'),
    path('add_async', views.add_async, name='add_async'),
] + staticfiles_urlpatterns()
