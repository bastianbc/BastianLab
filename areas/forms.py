from django import forms
from .models import *
from libprep.models import NucAcids
from method.models import Method
from core.forms import BaseForm


class AreaForm(BaseForm, forms.ModelForm):
    class Meta:
        model = Areas
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(AreaForm, self).__init__(*args, **kwargs)
        self.fields["block"].widget.attrs.update({'class':'form-control-sm'})
        self.fields["block"].widget.attrs["data-control"] = "select2"

class ExtractionOptionsForm(forms.Form):
    na_type = forms.ChoiceField(choices = NucAcids.NA_TYPES)
    extraction_method = forms.ModelChoiceField(queryset = Method.objects.all() )
