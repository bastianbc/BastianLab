from django.urls import path
from . import views
# from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path("login",views.log_in,name="login"),
    path("logout",views.log_out,name="logout"),
    path("set_password", views.set_password, name="set-password"),
    path("change_password", views.change_password, name="change-password"),
] + staticfiles_urlpatterns()
