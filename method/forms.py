from django import forms
from .models import *

class MethodForm(forms.ModelForm):
    class Meta:
        model = Method
        fields = ("name",)
