from django.urls import path
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
print(staticfiles_urlpatterns())
urlpatterns = [
    path("", views.barcodesets, name="barcodesets"),
    path("new", views.new_barcodeset, name="new-barcodeset"),
    path("edit/<int:id>", views.edit_barcodeset, name="edit-barcodeset"),
    path("delete/<int:id>", views.delete_barcodeset, name="delete-barcodeset"),
    path("filter_barcodesets", views.filter_barcodesets, name="filter-barcodesets"),
    path("<int:id>/barcodes", views.barcodes, name="barcodes"),
    path("<int:id>/activate", views.activate, name="active"),
    path("filter_barcodes", views.filter_barcodes, name="filter-barcodes"),
    path("edit_barcode_async", views.edit_barcode_async, name="edit-barcode-async"),
] + staticfiles_urlpatterns()
print(urlpatterns)
