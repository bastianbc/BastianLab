from django import forms
from .models import NucAcids
from barcodeset.models import Barcode
from django.core.exceptions import ValidationError
from core.forms import BaseForm


class NucAcidForm(BaseForm, forms.ModelForm):
    amount = forms.FloatField()

    class Meta:
        model = NucAcids
        fields = ("area", "name", "date", "method", "na_type", "conc", "vol_init", "vol_remain", "notes", )

    def __init__(self, *args, **kwargs):
        super(NucAcidForm, self).__init__(*args, **kwargs)
        self.fields["name"].required = False


class SampleLibCreationOptionsForm(forms.Form):
    barcode_start_with = forms.ModelChoiceField(queryset = Barcode.objects.filter(barcode_set__active=True))
    target_amount = forms.FloatField()
    shear_volume = forms.FloatField()
    prefix = forms.CharField()

class FilterForm(forms.Form):
    date_range = forms.DateField()
    na_type = forms.ChoiceField(choices=[('','---------' )] + NucAcids.NA_TYPES[:-1], label="NA Type", required=False)

    def __init__(self, *args, **kwargs):
        super(FilterForm, self).__init__(*args, **kwargs)
        self.fields["date_range"].widget.attrs.update({'class':'form-control-sm'})
        self.fields["na_type"].widget.attrs.update({'class':'form-control-sm'})
