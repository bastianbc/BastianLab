from django.urls import path
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path("", views.patients, name="patients"),
    path("filter_patients", views.filter_patients, name="filter-patients"),
    path('new', views.new_patient, name='new-patient'),
    path('edit/<str:id>', views.edit_patient, name='edit-patient'),
    path("edit_patient_async", views.edit_patient_async, name="edit-patient-async"),
    path('delete/<str:id>', views.delete_patient, name='delete-patient'),
    path("get_race_options", views.get_race_options, name="get-race-options"),
    path("get_sex_options", views.get_sex_options, name="get-sex-options"),
    path("export_csv_all_data", views.export_csv_all_data, name="export-csv-all-data"),
] + staticfiles_urlpatterns()
