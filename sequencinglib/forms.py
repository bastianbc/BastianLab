from django import forms
from .models import *
from datetime import date
from sequencingrun.models import SequencingRun

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

class SequencingLibAddForm(forms.Form):
    seq_run = forms.ModelChoiceField(queryset=SequencingRun.objects.all().order_by("name"), label="Sequencing Runs")
