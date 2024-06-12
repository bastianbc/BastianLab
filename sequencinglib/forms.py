from django import forms
from .models import *
from datetime import date
from sequencingrun.models import SequencingRun
from capturedlib.models import CapturedLib
from core.forms import BaseForm

class SequencingLibForm(BaseForm, forms.ModelForm):
    class Meta:
        model = SequencingLib
        fields = "__all__"

    captured_lib = forms.ModelMultipleChoiceField(
        queryset=CapturedLib.objects.all(),
        label="Captured Library"
    )

    def __init__(self, *args, **kwargs):
        super(SequencingLibForm, self).__init__(*args, **kwargs)
        self.fields['captured_lib'].required = False

        if self.instance.pk:
            self.fields['captured_lib'].initial = self.instance.cl_seql_links.values_list('captured_lib', flat=True)

    def save(self, commit=True):
        instance = super(SequencingLibForm, self).save(commit=False)
        if commit:
            instance.save()
        CL_SEQL_LINK.objects.filter(sequencing_lib=instance).delete()
        for cl in self.cleaned_data['captured_lib']:
            CL_SEQL_LINK.objects.create(
                sequencing_lib=instance,
                captured_lib=cl,
                volume=0
            )
        return instance

class SequencingLibRecreateForm(forms.Form):
    name = forms.CharField()
    date = forms.DateField(initial=date.today)
    buffer = forms.ChoiceField(choices=SequencingLib.BUFFER_TYPES)
    nm = forms.FloatField(initial=0, label="nM")
    vol_init = forms.FloatField(initial=0, label="Initialize Volume")

class SequencingLibAddForm(forms.Form):
    seq_run = forms.ModelChoiceField(queryset=SequencingRun.objects.all().order_by("name"), label="Sequencing Runs")
