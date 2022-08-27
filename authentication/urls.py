from django.urls import path
from . import views
# from django.contrib.auth import views as auth_views

urlpatterns = [
    path("login",views.log_in,name="login"),
    path("logout",views.log_out,name="logout"),
]
