from django import forms
from .models import SampleLib
from datetime import date
from buffer.models import Buffer

class SampleLibForm(forms.ModelForm):
    class Meta:
        model = SampleLib
        fields = "__all__"


class CapturedLibCreationOptionsForm(forms.Form):
    prefix = forms.CharField()
    date = forms.DateField(initial=date.today)
    bait = forms.ModelChoiceField(queryset=Buffer.objects.all())
