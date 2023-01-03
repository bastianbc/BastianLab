from django.urls import path
from django.conf import settings
from django.conf.urls import url
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static

urlpatterns = [
    path("", views.capturedlibs, name="capturedlibs"),
    path("filter_capturedlibs", views.filter_capturedlibs, name="filter-capturedlibs"),
    path("edit_capturedlib_async", views.edit_capturedlib_async, name="edit-capturedlib-async"),
    path('new', views.new_capturedlib, name='new-capturedlib'),
    path('new_async', views.new_capturedlib_async, name='new-capturedlib-async'),
    path('edit/<str:id>', views.edit_capturedlib, name='edit-capturedlib'),
    path('delete/<str:id>', views.delete_capturedlib, name='delete-capturedlib'),
    path('batch_delete', views.delete_batch_capturedlibs, name='delete-batch-capturedlibs'),
    path('<int:id>/used_samplelibs', views.get_used_samplelibs, name='get-used-samplelibs'),
    path('<int:id>/update_async', views.update_async, name='update_async'),
    path('check_idendical_barcode', views.check_idendical_barcode, name='check-identical-barcode'),
] + staticfiles_urlpatterns()
