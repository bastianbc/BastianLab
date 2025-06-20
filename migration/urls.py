from django.urls import path
from . import views

views = views

urlpatterns = [
    path("sequenced_files", views.sequenced_files, name="sequenced-files"),
    path("sequenced_files_opposite", views.sequenced_files_opposite, name="sequenced-files-opposite"),
    path("variant", views.variant, name="variant"),
    path("gene", views.gene, name="gene"),
    path("body_sites", views.import_body_sites, name="import-body-sites"),
    path("qpcr_consolidated_data", views.qpcr_consolidated_data, name="qpcr_consolidated_data"),
    path("qpcr_at_na", views.qpcr_at_na, name="qpcr_at_na"),
    path("qpcr_at_sl", views.qpcr_at_sl, name="qpcr_at_sl"),
    path("qpcr_at_seqrun", views.qpcr_at_seqrun, name="qpcr_at_seqrun"),
    path("import_body_sites", views.import_body_sites, name="import_body_sites"),
    path('import_genes', views.import_genes, name='import_genes'),
]
