from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required,permission_required
from account.models import User
from django.contrib.auth.forms import SetPasswordForm,PasswordChangeForm
from .forms import LoginForm, PasswordResetRequestForm, SetNewPasswordForm, SignUpForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from core.email_handler import send_email, get_superuser_emails
import logging

logger = logging.getLogger(__name__)


def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)

        if form.is_valid():
            user = form.save()

            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            activation_url = request.build_absolute_uri(
                reverse("activate-account", kwargs={"uidb64": uid, "token": token})
            )

            # ✅ Send activation email using centralized service
            send_email(
                subject="Activate Your Account - Bastian Lab",
                template_name="activation.html",
                recipients=[user.email],
                context={
                    "user": user.email,
                    "activation_url": activation_url,
                },
            )
            # --------------------
            # Admin notification
            # --------------------
            admin_emails = get_superuser_emails()
            print("admin_emails", admin_emails)
            if admin_emails:
                admin_edit_url = request.build_absolute_uri(
                    reverse("edit-account", kwargs={"id": user.id})
                )

                send_email(
                    subject="New User Registered - Action Required",
                    template_name="new_user_registered.html",
                    recipients=admin_emails,
                    context={
                        "new_user": user,
                        "admin_edit_url": admin_edit_url,
                    },
                    fail_silently=True,
                )
            messages.success(
                request,
                "Account created successfully. Please check your email to activate your account."
            )
            return redirect("/auth/login")

        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)

    else:
        form = SignUpForm()

    return render(request, "sign-up.html", {"form": form})



def log_in(request):
    if request.method == "POST":
        try:
            form = LoginForm(request.POST)

            username = request.POST.get("username")
            password = request.POST.get("password")
            next_url = request.GET.get("next")

            # ✅ Step 1: Find user first
            user_obj = User.objects.filter(username=username).first()

            if user_obj and not user_obj.is_active:
                messages.error(
                    request,
                    "Your account is not activated yet. Please check your email for the activation link."
                )
                return redirect("/auth/login")

            # ✅ Step 2: Authenticate only if active
            user = authenticate(username=username, password=password)

            if user:
                login(request, user)
                return redirect(next_url or settings.LOGIN_REDIRECT_URL)

            else:
                messages.error(request, "Invalid username or password.")

        except Exception:
            logger.exception("Login error")
            messages.error(request, "Unexpected error occurred.")

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


def forgot_password(request):
    if request.method == "POST":
        form = PasswordResetRequestForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data["email"]

            # 🔐 Do NOT leak whether user exists
            user = User.objects.filter(email=email, is_active=True).first()

            if user:
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))

                reset_url = request.build_absolute_uri(
                    reverse("reset-password", kwargs={"uidb64": uid, "token": token})
                )

                # ✅ Send branded reset email
                send_email(
                    subject="Reset Your Password - Bastian Lab",
                    template_name="password_reset.html",
                    recipients=[user.email],
                    context={
                        "user": user.email,
                        "reset_url": reset_url,
                    },
                )

            # Always show success message (even if user doesn't exist)
            messages.success(
                request,
                "If an account exists with this email, a password reset link has been sent."
            )
            return redirect("/auth/login")

    else:
        form = PasswordResetRequestForm()

    return render(request, "forgot-password.html", {"form": form})


def reset_password(request, uidb64, token):
    """Handle password reset with token"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == "POST":
            form = SetNewPasswordForm(request.POST)
            if form.is_valid():
                new_password = form.cleaned_data['new_password2']
                user.set_password(new_password)
                user.save()
                messages.success(request, "Your password has been reset successfully. You can now log in with your new password.")
                return redirect("/auth/login")
        else:
            form = SetNewPasswordForm()

        return render(request, "reset-password.html", {'form': form, 'validlink': True})
    else:
        messages.error(request, "The password reset link is invalid or has expired.")
        return render(request, "reset-password.html", {'validlink': False})


def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Your account has been activated successfully. You can now log in.")
        return redirect("/auth/login")
    else:
        messages.error(request, "Activation link is invalid or has expired.")
        return redirect("/auth/login")
