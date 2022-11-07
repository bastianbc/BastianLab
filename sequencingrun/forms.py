from django import forms
from .models import *
from datetime import date

class SequencingRunForm(forms.ModelForm):
    class Meta:
        model = SequencingRun
        fields = "__all__"

class SequencingRunCreationForm(forms.Form):
    prefix = forms.CharField()
    date_run = forms.DateField(initial=date.today)
    date = forms.DateField(initial=date.today)
    facility = forms.ChoiceField(choices=SequencingRun.FACILITY_TYPES)
    sequencer = forms.ChoiceField(choices=SequencingRun.SEQUENCER_TYPES)
    pe = forms.ChoiceField(choices=SequencingRun.PE_TYPES)
    amp_cycles = forms.IntegerField(initial=0)
