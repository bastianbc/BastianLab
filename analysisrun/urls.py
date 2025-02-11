from django.urls import path
from django.conf import settings

from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static

urlpatterns = [
    path("", views.analysisruns, name="analysisruns"),
    path("filter_analysisruns", views.filter_analysisruns, name="filter-analysisruns"),
    path('save_analysis_run', views.save_analysis_run, name='save-analysis-run'),
    path('process_variant/<str:variant_type>/<str:ar_name>', views.process_variant, name='process_variant'),
    path('import_cns/<str:ar_name>', views.import_cns, name='import_cns'),

] + staticfiles_urlpatterns()
