from django import forms
from datetime import date
from samplelib.models import SampleLib
from areas.models import Areas
from blocks.models import Blocks

class FilterForm(forms.Form):
    sample_lib = forms.CharField(label="Sample Library")
    area = forms.CharField()
    block = forms.CharField()

    def __init__(self, *args, **kwargs):
        super(FilterForm, self).__init__(*args, **kwargs)
        self.fields["sample_lib"].widget.attrs.update({'class':'form-control-sm'})
        self.fields["area"].widget.attrs.update({'class':'form-control-sm'})
        self.fields["block"].widget.attrs.update({'class':'form-control-sm'})
