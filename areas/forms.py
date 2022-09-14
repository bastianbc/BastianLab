from django import forms
from .models import *

class AreaForm(forms.ModelForm):
    class Meta:
        model = Areas
        fields = "__all__"

class AreaUpdateForm(forms.ModelForm):
    pass
