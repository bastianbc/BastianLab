from django import forms
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Max
from django.contrib.auth.models import Permission
from django.db.models import Q
from core.forms import BaseForm



User = get_user_model()

class CreateAccountForm(BaseForm):
    class Meta:
        model = get_user_model()
        fields = ("username","password","first_name","last_name","groups")
        widgets = {
            "password" : forms.PasswordInput()
        }

    def __init__(self, *args, **kwargs):
        super(CreateAccountForm, self).__init__(*args, **kwargs)
        self.fields["username"].required = True
        self.fields["password"].required = True
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

class EditAccountForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ("username","first_name","last_name","groups")

    def __init__(self, *args, **kwargs):
        super(EditAccountForm, self).__init__(*args, **kwargs)
        self.fields["username"].required = True
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True
