from django import forms
from .models import *

class SequencingLibForm(forms.ModelForm):
    class Meta:
        model = SequencingLib
        fields = "__all__"

class SequencingLibRecreateForm(forms.Form):
    # sequencing_lib = forms.ModelChoiceField(queryset=SequencingLib.objects.all(), label="Sequencing Library")
    name = forms.CharField()
    date = forms.DateField(initial=date.today)
    buffer = forms.ChoiceField(choices=SequencingLib.BUFFER_TYPES)
    conc = forms.FloatField(initial=0, label="Concentration")
    vol_init = forms.FloatField(initial=0, label="Initialize Volume")
