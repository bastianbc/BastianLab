from django.urls import path
from django.conf import settings
from django.conf.urls import url
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static

urlpatterns = [
    path("", views.genes, name="genes"),
    path("filter_genes", views.filter_genes, name="filter-genes"),
] + staticfiles_urlpatterns()
