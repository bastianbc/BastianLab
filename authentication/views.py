from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required,permission_required
from account.models import User
from django.contrib.auth.forms import SetPasswordForm,PasswordChangeForm
from .forms import LoginForm
import logging

logger = logging.getLogger(__name__)

def log_in(request):
    if request.method == "POST":
        try:
            form = LoginForm(request.POST)

            username = request.POST.get("username")
            password = request.POST.get("password")
            next = request.GET.get('next')
            user = authenticate(username=username, password=password)

            if user:
                login(request, user)
                if next:
                    return redirect(next)
                else:
                    return redirect(settings.LOGIN_REDIRECT_URL)
            else:
                user = User.objects.filter(username=username,last_login__isnull=True)
                if user.exists():
                    request.session["username"] = username
                    return redirect("/auth/set_password")
                else:
                    messages.error(request, "Invalid username or password!")
                messages.error(request, "Authentication Error!")
        except Exception as e:
            messages.error(request, "Unexpected Error!")
            print(e)
    else:
        form = LoginForm()

    return render(request, "sign-in.html", locals())

def log_out(request):
    logout(request)
    return redirect("/auth/login")

@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(user=request.user,data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Password changed successfully")
            return redirect("/")
        else:
            messages.error(request,"Password could not be changed!")
    else:
        form = PasswordChangeForm(user=request.user)

    return render (request,"change-password.html",locals())

def set_password(request):
    print(request.user)
    print(request.session)
    print(request.GET)
    print(request.POST)
    # user = User.objects.get(username=request.session["username"])
    user = request.user
    if request.method == "POST":
        form = SetPasswordForm(user=user,data=request.POST)
        if form.is_valid():
            form.save()
            login(request,user)
            messages.success(request,"Password set successfully")
            return redirect("/")
        else:
            messages.error(request,"Password could not be set!")
    else:
        form = SetPasswordForm(user=user)

    return render(request,"new-password.html",locals())
