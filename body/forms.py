from django import forms
from .models import *

class BodyForm(forms.ModelForm):
    class Meta:
        model = Body
        fields = ("name",)
