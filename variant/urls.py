from django.urls import path
from django.conf import settings
from django.conf.urls import url
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static

urlpatterns = [
    path("", views.variants, name="variants"),
    path("call", views.variant_calls, name="variant-calls"),
    path("g_variant", views.g_variants, name="g-variants"),
    path("c_variant", views.c_variants, name="c-variants"),
    path("p_variant", views.p_variants, name="p-variants"),
] + staticfiles_urlpatterns()
