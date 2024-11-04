from django import forms
from core.forms import BaseForm
from account.models import User

class LoginForm(BaseForm):
    class Meta:
        model = User
        fields = ['username', 'password']
        widgets = {
            'password': forms.PasswordInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] += ' bg-transparent'
        self.fields['username'].widget.attrs['placeholder'] = 'Username'

        self.fields['password'].widget.attrs['class'] += ' bg-transparent'
        self.fields['password'].widget.attrs['placeholder'] = 'Password'
