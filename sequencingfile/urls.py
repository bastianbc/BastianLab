from django.urls import path
from django.conf import settings
from django.conf.urls import url
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
] + staticfiles_urlpatterns()
