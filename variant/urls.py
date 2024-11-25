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
    path('get_variants_by_area', views.get_variants_by_area, name='get-variants-by-area'),
    path('get_variants_by_block', views.get_variants_by_block, name='get-variants-by-block'),
] + staticfiles_urlpatterns()
