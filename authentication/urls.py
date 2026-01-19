from django.urls import path
from . import views
# from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path("login",views.log_in,name="login"),
    path("logout",views.log_out,name="logout"),
    path("set_password", views.set_password, name="set-password"),
    path("change_password", views.change_password, name="change-password"),
    path("forgot_password", views.forgot_password, name="forgot_password"),
    path("reset_password/<uidb64>/<token>/", views.reset_password, name="reset-password"),
    path("signup/", views.signup, name="signup"),
    path("activate/<uidb64>/<token>/", views.activate_account, name="activate-account"),
] + staticfiles_urlpatterns()
