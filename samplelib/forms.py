from django import forms
from .models import SampleLib
from datetime import date
from capturedlib.models import CapturedLib

class SampleLibForm(forms.ModelForm):
    class Meta:
        model = SampleLib
        fields = "__all__"


class CapturedLibCreationOptionsForm(forms.Form):
    prefix = forms.CharField()
    date = forms.DateField(initial=date.today)
    bait = forms.ChoiceField(choices=CapturedLib.BAIT_TYPES)
