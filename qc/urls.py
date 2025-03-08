from django.urls import path
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path("", views.analysisruns, name="analysisruns"),
    path("filter_sampleqc", views.sample_qcs, name="filter-sampleqc"),
    path('import_qc/<str:ar_name>', views.import_qc, name='import_qc'),

] + staticfiles_urlpatterns()
