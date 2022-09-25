from django.urls import path
from . import views
from .views import BlockCreate
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    # path('', views.get_name),
    #path('addpatient/', views.get_patient, name='addpatient'),
    # path('patientlist/show/<pk>', PatientView.as_view(), name='patient-detail'),
    # path('patientlist/', PatientList.as_view(), name='patients-list'),
    # path('blocks/add/', BlockCreate.as_view(), name='block-add'),
    # path('patient/search/', PatientSearch.as_view(), name='patient-search'),
    #path('patientlist/<pk>/', PatientView.as_view(), name='patient-update'),
    # path('patientlist/<pk>/', PatientUpdate.as_view(), name='patient-update'),
    # path('patientlist/<pk>/delete/', PatientDelete.as_view(), name='patient-delete'),
    # #path('', views.quote_req, name='quote-request'),
    #$path('show/<int:pk>', QuoteView.as_view(), name='quote-detail'),
    #path('show', QuoteList.as_view(), name='showquotes'),
    path("", views.blocks, name="blocks"),
    path("filter_blocks", views.filter_blocks, name="filter-blocks"),
    path('new', views.new_block, name='new-block'),
    path('add_block_to_patient_async', views.add_block_to_patient_async, name='add-block-to-patient-async'),
    path('add_block_to_project_async', views.add_block_to_project_async, name='add-block-to-project-async'),
    path('edit/<str:id>', views.edit_block, name='edit-block'),
    path("edit_block_async", views.edit_block_async, name="edit-block-async"),
    path('delete/<str:id>', views.delete_block, name='delete-block'),
] + staticfiles_urlpatterns()
