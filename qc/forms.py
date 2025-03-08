from django import forms
from .models import SampleQC

class SampleQCForm(forms.ModelForm):
    class Meta:
        model = SampleQC
        fields = '__all__'
