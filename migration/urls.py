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
    path("consolidated_data", views.consolidated_data, name="consolidated-data"),
    path("body_sites", views.import_body_sites, name="import-body-sites"),
    path("airtable", views.airtable_consolidated_data, name="airtable-consolidated-data"),
    path("qpcr_consolidated_data", views.qpcr_consolidated_data, name="qpcr_consolidated_data"),
    path("qpcr_at_na", views.qpcr_at_na, name="qpcr_at_na"),
    path("qpcr_at_sl", views.qpcr_at_sl, name="qpcr_at_sl"),
    path("create_file_from_file", views.create_file_from_file, name="create_file_from_file"),
    path("qpcr_at_seqrun", views.qpcr_at_seqrun, name="qpcr_at_seqrun"),
]
