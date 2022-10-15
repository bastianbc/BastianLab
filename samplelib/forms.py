from django import forms
from .models import SampleLib

class SampleLibForm(forms.ModelForm):
    class Meta:
        model = SampleLib
        fields = "__all__"
