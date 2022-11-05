from django import forms
from .models import *

class SequencingLibForm(forms.ModelForm):
    class Meta:
        model = SequencingLib
        fields = "__all__"

class SequencingLibRecreateForm(forms.Form):
    name = forms.CharField()
    date = forms.DateField(initial=date.today)
    buffer = forms.ChoiceField(choices=SequencingLib.BUFFER_TYPES)
    nm = forms.FloatField(initial=0, label="nM")
    vol_init = forms.FloatField(initial=0, label="Initialize Volume")
