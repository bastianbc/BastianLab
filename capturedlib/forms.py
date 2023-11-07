from django import forms
from datetime import date
from .models import CapturedLib
from sequencinglib.models import SequencingLib

class CapturedLibForm(forms.ModelForm):
    class Meta:
        model = CapturedLib
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(CapturedLibForm, self).__init__(*args, **kwargs)
        self.fields["nm"].required = False

class SequencingLibCreationForm(forms.Form):
    sequencing_lib = forms.ModelChoiceField(queryset=SequencingLib.objects.all(), label="Sequencing Library")
    prefix = forms.CharField()
    date = forms.DateField(initial=date.today)
    buffer = forms.ChoiceField(choices=SequencingLib.BUFFER_TYPES)
    nm = forms.FloatField(initial=0, label="nM")
    vol_init = forms.FloatField(initial=0, label="Initialize Volume")
