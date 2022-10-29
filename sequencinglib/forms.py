from django import forms
from .models import *

class SequencingLibForm(forms.ModelForm):
    class Meta:
        model = SequencingLib
        fields = "__all__"
