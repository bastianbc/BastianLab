from django.urls import path
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path("", views.blocks, name="blocks"),
    path("filter_blocks", views.filter_blocks, name="filter-blocks"),
    path('new', views.new_block, name='new-block'),
    path('add_block_to_patient_async', views.add_block_to_patient_async, name='add-block-to-patient-async'),
    path('add_block_to_project_async', views.add_block_to_project_async, name='add-block-to-project-async'),
    path('remove_block_from_project_async', views.remove_block_from_project_async, name='remove-block-from-project-async'),
    path('remove_block_from_patient_async', views.remove_block_from_patient_async, name='remove-block-from-patient-async'),
    path('edit/<str:id>', views.edit_block, name='edit-block'),
    path("edit_block_async", views.edit_block_async, name="edit-block-async"),
    path('delete/<str:id>', views.delete_block, name='delete-block'),
    path('batch_delete', views.delete_batch_blocks, name='delete-batch-blocks'),
    path('check_can_deleted_async', views.check_can_deleted_async, name='checkcan-deleted-async'),
    path("get_block_async", views.get_block_async, name='get-get_block_async'),
    path("export_csv_all_data", views.export_csv_all_data, name="export-csv-all-data"),
    path("edit_block_url", views.edit_block_url, name="edit_block_url"),
    path("get_block_vaiants", views.get_block_vaiants, name="get_block_vaiants"),
    path("get_block_areas/<int:id>/", views.get_block_areas, name="get-block-areas"),
] + staticfiles_urlpatterns()
