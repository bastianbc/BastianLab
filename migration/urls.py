from django.urls import path
from . import views

urlpatterns = [
    path("", views.migrate, name="migrate"),
    path("report", views.report, name="report"),
    path("sequenced_files", views.sequenced_files, name="sequenced_files"),
]
