from django import forms
from datetime import date
from samplelib.models import SampleLib
from areas.models import Area
from blocks.models import Block
from sequencingrun.models import SequencingRun
from lab.models import Patient

class FilterForm(forms.Form):
    sequencing_run=forms.ModelChoiceField(
        queryset=SequencingRun.objects.filter(variant_calls__isnull=False).distinct(),
        label="Sequencing Run"
    )
    sample_lib=forms.ModelChoiceField(
        queryset=SampleLib.objects.filter(variant_calls__isnull=False).distinct(),
        label="Sample Library"
    )
    area=forms.ModelChoiceField(
        queryset=Area.objects.filter(area_na_links__nucacid__na_sl_links__sample_lib__variant_calls__isnull=False).distinct(),
        label="Areas"
    )
    block=forms.ModelChoiceField(
        queryset=Block.objects.filter(block_areas__area_na_links__nucacid__na_sl_links__sample_lib__variant_calls__isnull=False).distinct(),
        label="Blocks"
    )
    patient=forms.ModelChoiceField(
        queryset=Patient.objects.filter(
            patient_blocks__block_areas__area_na_links__nucacid__na_sl_links__sample_lib__variant_calls__isnull=False
        ).distinct(),
        label="Patients"
    )
    coverage = forms.IntegerField(label="Coverage")
    log2r = forms.FloatField(label="Log2r")
    ref_read = forms.IntegerField(label="Ref Read")
    alt_read = forms.IntegerField(label="Alt Read")

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
        self.fields["coverage"].widget.attrs.update({'class':'form-control-sm'})
        self.fields["log2r"].widget.attrs.update({'class':'form-control-sm'})
        self.fields["ref_read"].widget.attrs.update({'class':'form-control-sm'})
        self.fields["alt_read"].widget.attrs.update({'class':'form-control-sm'})
