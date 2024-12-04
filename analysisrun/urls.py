from django.urls import path
from django.conf import settings
from django.conf.urls import url
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static

urlpatterns = [
    path("", views.analysisruns, name="analysisruns"),
    path("filter_analysisruns", views.filter_analysisruns, name="filter-analysisruns"),
    path('save_analysis_run', views.save_analysis_run, name='save-analysis-run'),
] + staticfiles_urlpatterns()
