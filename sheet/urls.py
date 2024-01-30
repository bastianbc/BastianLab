from django.urls import path
from django.conf import settings
from django.conf.urls import url
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static

urlpatterns = [
    path("", views.get_sheet, name="get_sheet"),
    path("filter_sheet", views.filter_sheet, name="filter_sheet"),
    path("create_csv_sheet", views.create_csv_sheet, name="create_csv_sheet"),
] + staticfiles_urlpatterns()
