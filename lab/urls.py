from django.urls import path
from django.conf import settings
from django.conf.urls import url
from django.views.static import serve
from . import views
from .views import PatientList, PatientCreate, PatientUpdate, \
     PatientDelete, PatientsBlocksUpdateView
from .forms import PatientForm


# urlpatterns = [
#     path('', views.quote_req, name='quote-request'),
#     path('show', QuoteList.as_view(), name='showquotes')
# ]


urlpatterns = [
    # path('', views.get_name),
    #path('addpatient/', views.get_patient, name='addpatient'),
    # path('patientlist/show/<pk>', PatientView.as_view(), name='patient-detail'),
    path('', PatientList.as_view(), name='patients-list'),
    path('patient/add/', PatientCreate.as_view(), name='patient-add'),
    # path('patient/search/', PatientSearch.as_view(), name='patient-search'),
    path('patient/<pk>/', PatientUpdate.as_view(), name='patient-update'),
    # path('patientlist/<pk>/', PatientsBlocksUpdateView.as_view(), name='block-update'),
    path('patient/delete/<pk>', PatientDelete.as_view(), name='patient-delete'),
    # path('areaslist/', AreasList.as_view(), name='areas-list'),
    #path('', views.quote_req, name='quote-request'),
    #$path('show/<int:pk>', QuoteView.as_view(), name='quote-detail'),
    #path('show', QuoteList.as_view(), name='showquotes'),
]
if settings.DEBUG:
    urlpatterns = [
        url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT,}),
        # For django versions before 2.0:
        # url(r'^__debug__/', include(debug_toolbar.urls)),

    ] + urlpatterns
