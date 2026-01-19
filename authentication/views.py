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
from core.email_handler import send_email
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
            next = request.GET.get("next")

            user = authenticate(username=username, password=password)

            if user:
                if not user.is_active:
                    messages.error(
                        request,
                        "Your account is not activated yet. Please check your email for the activation link."
                    )
                    return redirect("/auth/login")

                login(request, user)
                return redirect(next or settings.LOGIN_REDIRECT_URL)

            else:
                messages.error(request, "Invalid username or password.")

        except Exception as e:
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
    """Handle password reset request"""
    if request.method == "POST":
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.get(email=email)

            # Generate token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            # Build reset URL
            reset_url = request.build_absolute_uri(
                reverse('reset-password', kwargs={'uidb64': uid, 'token': token})
            )

            # Send email
            subject = 'Password Reset Request - Bastian Lab'
            message = render_to_string('password_reset_email.html', {
                'user': user,
                'reset_url': reset_url,
            })

            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                messages.success(request, "Password reset link has been sent to your email address.")
                return redirect("/auth/login")
            except Exception as e:
                logger.error(f"Failed to send password reset email: {e}")
                messages.error(request, "Failed to send email. Please try again later.")
    else:
        form = PasswordResetRequestForm()

    return render(request, "forgot-password.html", locals())


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
