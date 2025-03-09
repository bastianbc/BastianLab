from django.urls import path
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path("", views.sample_qcs, name="sample_qcs"),
    path("filter_sampleqcs", views.filter_sampleqcs, name="filter-sampleqc"),
    path('process/<str:ar_name>', views.process_qc_metrics, name='process-qc-metrics'),
    path("detail/<int:pk>", views.get_sampleqc_detail, name="get-sampleqc-detail"),
    path('pdf/<int:pk>', views.serve_pdf, name='serve_pdf'),


] + staticfiles_urlpatterns()
