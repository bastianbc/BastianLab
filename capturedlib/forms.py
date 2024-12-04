from django import forms
from datetime import date
from core.forms import BaseForm
from .models import CapturedLib, SL_CL_LINK
from sequencinglib.models import SequencingLib
from samplelib.models import SampleLib

class CapturedLibForm(BaseForm, forms.ModelForm):
    class Meta:
        model = CapturedLib
        fields = "__all__"

    sample_lib = forms.ModelMultipleChoiceField(
        queryset=SampleLib.objects.all(),
        label="Sample Library"
    )
    def __init__(self, *args, **kwargs):
        super(CapturedLibForm, self).__init__(*args, **kwargs)
        self.fields["nm"].required = False
        self.fields['sample_lib'].required = False

        if self.instance.pk:
            self.fields['sample_lib'].initial = self.instance.sl_cl_links.values_list('sample_lib', flat=True)

    def save(self, commit=True):
        instance = super(CapturedLibForm, self).save(commit=False)
        if commit:
            instance.save()
        SL_CL_LINK.objects.filter(captured_lib=instance).delete()
        for sl in self.cleaned_data['sample_lib']:
            SL_CL_LINK.objects.create(
                captured_lib=instance,
                sample_lib=sl,
                volume=0
            )
        return instance

class SequencingLibCreationForm(forms.Form):
    sequencing_lib = forms.ModelChoiceField(queryset=SequencingLib.objects.all().order_by("name"), label="Sequencing Library")
    prefix = forms.CharField()
    date = forms.DateField(initial=date.today)
    buffer = forms.ChoiceField(choices=SequencingLib.BUFFER_TYPES)
    nm = forms.FloatField(initial=0, label="nM")
    vol_init = forms.FloatField(initial=0, label="Initialize Volume")
