from django.urls import path
from django.conf import settings
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static

urlpatterns = [
    path("", views.analysisruns, name="analysisruns"),
    path("filter_analysisruns", views.filter_analysisruns, name="filter-analysisruns"),
    path('save_analysis_run', views.save_analysis_run, name='save-analysis-run'),
    path('initialize_import_variants/<str:ar_name>/', views.initialize_import_variants, name='initialize-import-variants'),
    path('get_import_status/<str:ar_name>/', views.get_import_status, name='get-import-status'),
    path('delete/<str:id>', views.delete_analysis_run, name='delete-analysis-run'),
    path('batch_delete', views.delete_batch_analysis_run, name='delete-batch-analysis-run'),
    path('check_can_deleted_async', views.check_can_deleted_async, name='check-can-deleted-async'),
] + staticfiles_urlpatterns()
