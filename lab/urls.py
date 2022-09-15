from django.urls import path
from django.conf import settings
from django.conf.urls import url
from django.views.static import serve
from . import views
from .views import PatientUpdate, PatientDelete, PatientsBlocksUpdateView
from .forms import PatientForm
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# urlpatterns = [
#     path('', views.quote_req, name='quote-request'),
#     path('show', QuoteList.as_view(), name='showquotes')
# ]


urlpatterns = [
    # path('', views.get_name),
    #path('addpatient/', views.get_patient, name='addpatient'),
    # path('patientlist/show/<pk>', PatientView.as_view(), name='patient-detail'),
    # path('', PatientList.as_view(), name='patients-list'),
    path("", views.patients, name="patients"),
    path("filter_patients", views.filter_patients, name="filter-patients"),
    path('new', views.new_patient, name='new-patient'),
    path('edit/<str:id>', views.edit_patient, name='edit-patient'),
    path("edit_patient_async", views.edit_patient_async, name="edit-patient-async"),
    path('delete/<str:id>', views.delete_patient, name='delete-patient'),
    # path('patient/search/', PatientSearch.as_view(), name='patient-search'),
    path('patient/<pk>/', PatientUpdate.as_view(), name='patient-update'),
    # path('patientlist/<pk>/', PatientsBlocksUpdateView.as_view(), name='block-update'),
    path('patient/delete/<pk>', PatientDelete.as_view(), name='patient-delete'),
    # path('areaslist/', AreasList.as_view(), name='areas-list'),
    #path('', views.quote_req, name='quote-request'),
    #$path('show/<int:pk>', QuoteView.as_view(), name='quote-detail'),
    #path('show', QuoteList.as_view(), name='showquotes'),
] + staticfiles_urlpatterns()
