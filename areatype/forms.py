from django import forms
from .models import *

class AreaTypeForm(forms.ModelForm):
    class Meta:
        model = AreaType
        fields = ("value","name")
