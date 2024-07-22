from django import forms
from .models import *
from datetime import date, datetime
from core.forms import BaseForm

class SequencingRunForm(BaseForm):
    class Meta:
        model = SequencingRun
        fields = "__all__"

class SequencingRunCreationForm(forms.Form):
    prefix = forms.CharField()
    date_run = forms.DateTimeField(initial=datetime.now)
    date = forms.DateField(initial=date.today)
    facility = forms.ChoiceField(choices=SequencingRun.FACILITY_TYPES)
    sequencer = forms.ChoiceField(choices=SequencingRun.SEQUENCER_TYPES)
    pe = forms.ChoiceField(choices=SequencingRun.PE_TYPES)
    amp_cycles = forms.IntegerField(initial=0)

class AnalysisRunForm(BaseForm):
    sheet_content = forms.CharField(widget=forms.HiddenInput())

    class Meta:
        model = AnalysisRun
        fields = ("user", "pipeline", "genome")
        widgets = {
            "user": forms.HiddenInput(),
        }
