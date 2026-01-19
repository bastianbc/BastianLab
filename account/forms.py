from django import forms
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Max
from django.contrib.auth.models import Permission
from django.db.models import Q
from core.forms import BaseForm

User = get_user_model()


class EmailValidationMixin:
    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip().lower()

        if not email:
            raise forms.ValidationError("Email is required.")

        # Uniqueness check
        qs = User.objects.filter(email__iexact=email)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError("This email is already registered.")

        return email

    def clean(self):
        cleaned = super().clean()
        username = cleaned.get("username", "")
        email = cleaned.get("email", "")

        # If username looks like email, enforce consistency
        if "@" in username and username.lower() != email.lower():
            raise forms.ValidationError(
                "Username and email must match when username is an email address."
            )

        return cleaned

class CreateAccountForm(BaseForm, EmailValidationMixin):
    class Meta:
        model = get_user_model()
        fields = ("username","email","password","first_name","last_name","groups")
        widgets = {
            "password" : forms.PasswordInput()
        }

    def __init__(self, *args, **kwargs):
        super(CreateAccountForm, self).__init__(*args, **kwargs)
        self.fields["username"].required = True
        self.fields["password"].required = True
        self.fields["email"].required = True
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True

    def save(self, commit=True):
        user = super(CreateAccountForm, self).save(commit=False)

        # Check if the ID is already used
        with transaction.atomic():
            max_id = self.Meta.model.objects.aggregate(max_id=Max('id'))['max_id'] or 0
            while self.Meta.model.objects.filter(id=max_id + 1).exists():
                max_id += 1
            user.id = max_id + 1

        if commit:
            user.save()
            self.save_m2m()  # Required for saving ManyToMany relations

            # Assign permissions except delete permissions
            permissions = Permission.objects.filter(~Q(codename__contains='delete'))
            user.user_permissions.set(permissions)

        return user

class EditAccountForm(BaseForm, EmailValidationMixin):
    class Meta:
        model = get_user_model()
        fields = ("username","email","first_name","last_name","groups")

    def __init__(self, *args, **kwargs):
        super(EditAccountForm, self).__init__(*args, **kwargs)
        self.fields["username"].required = True
        self.fields["email"].required = True
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True
