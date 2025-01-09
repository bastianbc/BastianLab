from django.urls import path
from django.conf import settings
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static

urlpatterns = [
    path("", views.cnses, name="cnses"),
    path("filter_cnses", views.filter_cnses, name="filter-cnses"),
] + staticfiles_urlpatterns()
