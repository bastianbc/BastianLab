from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class CreateAccountForm(forms.ModelForm):
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

class EditAccountForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ("username","first_name","last_name","groups")

    def __init__(self, *args, **kwargs):
        super(EditAccountForm, self).__init__(*args, **kwargs)
        self.fields["username"].required = True
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True
