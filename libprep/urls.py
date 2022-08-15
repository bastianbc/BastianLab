from django.urls import path
from django.conf import settings
from django.conf.urls import url
from django.views.static import serve
from . import views
from .views import AreaList, edit_nucacids, NucAcidsList, NucAcidUpdate, \
    NucAcidDelete, extract_nucacids


urlpatterns = [
    path('arealist/', AreaList.as_view(), name='areas-list'),
    # path('patient/add/', PatientCreate.as_view(), name='patient-add'),
    # # path('patient/search/', PatientSearch.as_view(), name='patient-search'),
    # path('patient/<pk>/', PatientUpdate.as_view(), name='patient-update'),
    path('nucacids_entry/', edit_nucacids, name='nucacids-update'),
    path('nucacids_list/', NucAcidsList.as_view(), name='nucacids-list'),
    path('nucacids_list/<int:pk>', NucAcidUpdate.as_view(), name='nucacid_update_single'),
    path('nucacid/delete/<pk>', NucAcidDelete.as_view(), name='nucacid-delete'),
    path('nucacids/extract/', extract_nucacids, name='extract_nucacids')
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
