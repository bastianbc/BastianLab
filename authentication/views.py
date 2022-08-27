from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages

def log_in(request):
    if request.method == "POST":
        try:
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
                messages.error(request, "Authentication Error!")
                print("Authentication Error!")
        except Exception as e:
            messages.error(request, "Unexpected Error!")
            print("Unexpected Error!")

    return render(request, "sign-in.html", locals())

def log_out(request):
    logout(request)
    return redirect("/")
