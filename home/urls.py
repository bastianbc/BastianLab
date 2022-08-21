from django.urls import path
from . import views
from django.views.generic.base import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='/dashboard'), name='index'),
    path('dashboard/', views.Dashboard.as_view(), name='dashboard'),
]
