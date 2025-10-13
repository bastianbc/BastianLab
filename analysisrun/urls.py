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
] + staticfiles_urlpatterns()
