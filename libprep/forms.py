from django import forms
from .models import NucAcids
from samplelib.models import Barcode
from django.core.exceptions import ValidationError

class NucAcidForm(forms.ModelForm):
    amount = forms.FloatField()

    class Meta:
        model = NucAcids
        fields = ("area", "name", "date", "method", "na_type", "conc", "vol_init", "vol_remain", "notes", )

    def __init__(self, *args, **kwargs):
        super(NucAcidForm, self).__init__(*args, **kwargs)
        self.fields["name"].required = False

class SampleLibCreationOptionsForm(forms.Form):
    barcode_start_with = forms.ModelChoiceField(queryset = Barcode.objects.all())
    target_amount = forms.FloatField()
    share_volume = forms.FloatField()
    prefix = forms.CharField()
