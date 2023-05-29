from django.urls import path
from . import views

urlpatterns = [
    path("", views.migrate, name="migrate"),
    path("report", views.report, name="report"),
    path("sequenced_files", views.sequenced_files, name="sequenced-files"),
    path("sequenced_files_opposite", views.sequenced_files_opposite, name="sequenced-files-opposite"),
    path("variant", views.variant, name="variant"),
    path("gene", views.gene, name="gene"),
    path("lookup", views.lookup_all_data, name="lookup-all-data"),
]
