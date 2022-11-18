from django import forms
from .models import NucAcids
from samplelib.models import Barcode

class NucAcidForm(forms.ModelForm):
    amount = forms.FloatField()
    class Meta:
        model = NucAcids
        fields = "__all__"

class SampleLibCreationOptionsForm(forms.Form):
    barcode_start_with = forms.ModelChoiceField(queryset = Barcode.objects.all())
    target_amount = forms.CharField()
    prefix = forms.CharField()
