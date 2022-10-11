from django import forms
from .models import *
from libprep.models import NucAcids
from method.models import Method

class AreaForm(forms.ModelForm):
    class Meta:
        model = Areas
        fields = "__all__"

class ExtractionOptionsForm(forms.Form):
    na_type = forms.ChoiceField(choices = NucAcids.NA_TYPES)
    extraction_method = forms.ModelChoiceField(queryset = Method.objects.all() )
