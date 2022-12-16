from django import forms
from datetime import date
from .models import CapturedLib
from sequencinglib.models import SequencingLib
from buffer.models import Buffer

class CapturedLibForm(forms.ModelForm):
    class Meta:
        model = CapturedLib
        fields = "__all__"

class SequencingLibCreationForm(forms.Form):
    sequencing_lib = forms.ModelChoiceField(queryset=SequencingLib.objects.all(), label="Sequencing Library")
    prefix = forms.CharField()
    date = forms.DateField(initial=date.today)
    buffer = forms.ModelChoiceField(queryset=Buffer.objects.all())
    nm = forms.FloatField(initial=0, label="nM")
    vol_init = forms.FloatField(initial=0, label="Initialize Volume")
