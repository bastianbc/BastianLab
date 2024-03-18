from django import forms
from .models import SampleLib
from datetime import date
from bait.models import Bait
from barcodeset.models import Barcode
from areas.models import Areas
from core.forms import BaseForm
from sequencingrun.models import SequencingRun
from capturedlib.models import CapturedLib

class SampleLibForm(BaseForm, forms.ModelForm):
    class Meta:
        model = SampleLib
        fields = "__all__"

class CapturedLibCreationOptionsForm(forms.Form):
    prefix = forms.CharField()
    date = forms.DateField(initial=date.today)
    bait = forms.ModelChoiceField(queryset=Bait.objects.all())

class FilterForm(forms.Form):
    sequencing_run = forms.ModelChoiceField(queryset=SequencingRun.objects.all().order_by("name"), label="Sequencing Run")
    # patient = forms.CharField()
    barcode = forms.ModelChoiceField(queryset=Barcode.objects.filter(barcode_set__active=True))
    i5 = forms.CharField()
    i7 = forms.CharField()
    area_type = forms.ChoiceField(choices=[('','---------' ),("normal","Normal"),("tumor","Tumor")], label="Area Type", required=False)
    bait = forms.ModelChoiceField(queryset=Bait.objects.all())

    def __init__(self, *args, **kwargs):
        super(FilterForm, self).__init__(*args, **kwargs)
        self.fields["sequencing_run"].widget.attrs.update({'class':'form-control-sm'})
        self.fields["sequencing_run"].widget.attrs["data-control"] = "select2"
        # self.fields["patient"].widget.attrs.update({'class':'form-control-sm'})
        self.fields["barcode"].widget.attrs.update({'class':'form-control-sm'})
        self.fields["i5"].widget.attrs.update({'class':'form-control-sm'})
        self.fields["i7"].widget.attrs.update({'class':'form-control-sm'})
        self.fields["area_type"].widget.attrs.update({'class':'form-control-sm'})
        self.fields["bait"].widget.attrs.update({'class':'form-control-sm'})


class CapturedLibAddForm(forms.Form):
    captured_lib = forms.ModelChoiceField(queryset=CapturedLib.objects.all().order_by("name"), label="Captured Libs")
