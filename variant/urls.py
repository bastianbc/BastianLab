from django.urls import path
from django.conf import settings
from django.conf.urls import url
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static

urlpatterns = [
    path("", views.variants, name="variants"),
    path("filter_variants", views.filter_variants, name="filter-variants"),
    path("import_variants/<str:name>", views.import_variants, name="import-variants"),
] + staticfiles_urlpatterns()
