from django.urls import path

from . import views
from .views import BlockCreate

urlpatterns = [
    # path('', views.get_name),
    #path('addpatient/', views.get_patient, name='addpatient'),
    # path('patientlist/show/<pk>', PatientView.as_view(), name='patient-detail'),
    # path('patientlist/', PatientList.as_view(), name='patients-list'),
    path('blocks/add/', BlockCreate.as_view(), name='block-add'),
    # path('patient/search/', PatientSearch.as_view(), name='patient-search'),
    #path('patientlist/<pk>/', PatientView.as_view(), name='patient-update'),
    # path('patientlist/<pk>/', PatientUpdate.as_view(), name='patient-update'),
    # path('patientlist/<pk>/delete/', PatientDelete.as_view(), name='patient-delete'),
    # #path('', views.quote_req, name='quote-request'),
    #$path('show/<int:pk>', QuoteView.as_view(), name='quote-detail'),
    #path('show', QuoteList.as_view(), name='showquotes'),
]