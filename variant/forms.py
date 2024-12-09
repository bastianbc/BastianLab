from django import forms
from datetime import date
from samplelib.models import SampleLib
from areas.models import Areas
from blocks.models import Blocks
from sequencingrun.models import SequencingRun
from lab.models import Patients

class FilterForm(forms.Form):
    sequencing_run = forms.ModelChoiceField(
        queryset=SequencingRun.objects.filter(variant_calls__isnull=False).distinct(),
        label="Sequencing Run"
    )
    sample_lib = forms.ModelChoiceField(
        queryset=SampleLib.objects.filter(variant_calls__isnull=False).distinct(),
        label="Sample Library"
    )
    area = forms.ModelChoiceField(
        queryset=Areas.objects.filter(
            area_na_links__nucacid__na_sl_links__sample_lib__variant_calls__isnull=False).distinct(),
        label="Areas"
    )
    block = forms.ModelChoiceField(
        queryset=Blocks.objects.filter(block_areas__area_na_links__nucacid__na_sl_links__sample_lib__variant_calls__isnull=False).distinct(),
        label="Blocks"
    )
    patient = forms.ModelChoiceField(
        queryset=Patients.objects.filter(patient_blocks__block_areas__area_na_links__nucacid__na_sl_links__sample_lib__variant_calls__isnull=False).distinct(),
        label="Patients"
    )


    def __init__(self, *args, **kwargs):
        super(FilterForm, self).__init__(*args, **kwargs)
        self.fields["patient"].widget.attrs.update({'class': 'form-control-sm'})
        self.fields["patient"].widget.attrs["data-control"] = "select2"
        self.fields["block"].widget.attrs.update({'class': 'form-control-sm'})
        self.fields["block"].widget.attrs["data-control"] = "select2"
        self.fields["sequencing_run"].widget.attrs.update({'class': 'form-control-sm'})
        self.fields["sequencing_run"].widget.attrs["data-control"] = "select2"
        self.fields["sample_lib"].widget.attrs.update({'class': 'form-control-sm'})
        self.fields["sample_lib"].widget.attrs["data-control"] = "select2"
        self.fields["area"].widget.attrs.update({'class': 'form-control-sm'})
        self.fields["area"].widget.attrs["data-control"] = "select2"

