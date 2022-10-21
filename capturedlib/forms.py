from django import forms
from .models import CapturedLib

class CapturedLibForm(forms.ModelForm):
    class Meta:
        model = CapturedLib
        fields = "__all__"
