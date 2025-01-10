from django import forms
from .models import *
from libprep.models import NucAcids
from method.models import Method
from core.forms import BaseForm
from areatype.models import AreaType

class AreaForm(BaseForm, forms.ModelForm):
    class Meta:
        model = Area
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(AreaForm, self).__init__(*args, **kwargs)
        self.fields["block"].widget.attrs.update({'class':'form-control-sm'})
        self.fields["block"].widget.attrs["data-control"] = "select2"
        self.fields["area_type"].queryset = AreaType.objects.all().order_by('name')
        self.fields["area_type"].widget.attrs.update({'class':'form-control-sm'})
        self.fields["area_type"].widget.attrs["data-control"] = "select2"


class ExtractionOptionsForm(forms.Form):
    na_type = forms.ChoiceField(choices = NucAcids.NA_TYPES)
    extraction_method = forms.ModelChoiceField(queryset = Method.objects.all() )
