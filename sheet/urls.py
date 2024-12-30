from django.urls import path
from django.conf import settings

from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static

urlpatterns = [
    path("", views.get_sheet, name="get_sheet"),
    path("filter_sheet", views.filter_sheet, name="filter_sheet"),
    path("alternative_export", views.alternative_export, name="alternative_export"),
    path("create_csv_sheet", views.create_csv_sheet, name="create_csv_sheet"),
    path("sheet_seq_run", views.sheet_seq_run, name="sheet_seq_run"),
    path("sheet_multiple", views.sheet_multiple, name="sheet_multiple"),
] + staticfiles_urlpatterns()
