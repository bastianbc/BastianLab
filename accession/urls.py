from django.urls import path
from accession.views import PartList, BlockList, addparts, BlockDelete
# from .forms import PatientForm

urlpatterns = [
    path('', PartList.as_view(), name='part-list'),
    path('partlist/<int:pk>/',PartList.as_view(), name='part-list'),
    # path(r'^partlist/(?P<pk>\d+)/$',PartList.as_view(), name='part-list'),
    path('addparts/', addparts, name='add-parts'),
    # path('partlookup/<int:associated_project>', partlookup, name='part-lookup'),
    path('blocklist/', BlockList.as_view(), name='block-list'),
    # path('blocklist/<int:projectid>', BlockList.as_view(), name='block_list2'),
    # path('block/update/<int:pk>/', BlockUpdate.as_view(), name='block-update'),
    path('block/delete/<int:pk>/', BlockDelete.as_view(), name='block-delete'),
    # path('area/add/<int:pk>/', AreaCreate.as_view(), name='add-areas'),
    # path('arealist/<int:pk>/',AreaUpdate.as_view(), name='area-update'),
    # path('area/delete/<int:pk>/', AreaDelete.as_view(), name='area-delete'),



]
