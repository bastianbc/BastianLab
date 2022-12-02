from django import forms
from .models import NucAcids
from samplelib.models import Barcode
from django.core.exceptions import ValidationError

class NucAcidForm(forms.ModelForm):
    amount = forms.FloatField()
    prefix = forms.CharField(max_length=10)

    class Meta:
        model = NucAcids
        fields = ("area", "date", "method", "na_type", "conc", "vol_init", "vol_remain", "notes", )

class SampleLibCreationOptionsForm(forms.Form):
    barcode_start_with = forms.ModelChoiceField(queryset = Barcode.objects.all())
    target_amount = forms.CharField()
    prefix = forms.CharField()
