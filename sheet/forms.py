from django import forms
from samplelib.models import SampleLib
from datetime import date
from bait.models import Bait
from barcodeset.models import Barcode
from areas.models import Areas
from core.forms import BaseForm
from sequencingrun.models import SequencingRun
from capturedlib.models import CapturedLib
from lab.models import Patients

class FilterForm(forms.Form):
    sequencing_run = forms.ModelMultipleChoiceField(queryset=SequencingRun.objects.all().order_by("name"), label="Sequencing Run")
    patient = forms.ModelChoiceField(queryset=Patients.objects.filter())
    barcode = forms.ModelChoiceField(queryset=Barcode.objects.filter())
    bait = forms.ModelChoiceField(queryset=Bait.objects.filter())
    area_type = forms.ChoiceField(choices=[('','---------' ),("normal","Normal"),("tumor","Tumor")], label="Area Type", required=False)
    na_type = forms.ChoiceField(choices=[('','---------' ),("dna","DNA"),("rna","RNA")], label="NA Type", required=False)

    def __init__(self, *args, **kwargs):
        super(FilterForm, self).__init__(*args, **kwargs)
        self.fields["sequencing_run"].widget.attrs.update({'class':'form-control-sm'})
        self.fields["sequencing_run"].widget.attrs["data-control"] = "select2"
        self.fields["patient"].widget.attrs.update({'class':'form-control-sm'})
        self.fields["patient"].widget.attrs["data-control"] = "select2"
        self.fields["barcode"].widget.attrs.update({'class':'form-control-sm'})
        self.fields["bait"].widget.attrs.update({'class':'form-control-sm'})
        self.fields["area_type"].widget.attrs.update({'class':'form-control-sm'})
        self.fields["na_type"].widget.attrs.update({'class':'form-control-sm'})


class ReportForm(forms.Form):
    sequencing_run = forms.ModelMultipleChoiceField(queryset=SequencingRun.objects.all().order_by("name"),
                                                    label="Sequencing Run")

    def __init__(self, *args, **kwargs):
        super(ReportForm, self).__init__(*args, **kwargs)
        self.fields["sequencing_run"].widget.attrs.update({'class':'form-control-sm'})
