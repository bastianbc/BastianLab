from django import forms
from datetime import date
from samplelib.models import SampleLib
from areas.models import Areas
from blocks.models import Blocks

class FilterForm(forms.Form):
    patient = forms.CharField()
    sample_lib = forms.CharField(label="Sample Library")
    area = forms.CharField()
    block = forms.CharField()
    coverage = forms.IntegerField(label="Coverage") #required=False,  is necessary?
    log2r = forms.FloatField(label="Log2r")
    ref_read = forms.IntegerField(label="Ref Read")
    alt_read = forms.IntegerField(label="Alt Read")

    def __init__(self, *args, **kwargs):
        super(FilterForm, self).__init__(*args, **kwargs)
        self.fields["patient"].widget.attrs.update({'class':'form-control-sm'})
        self.fields["sample_lib"].widget.attrs.update({'class':'form-control-sm'})
        self.fields["area"].widget.attrs.update({'class':'form-control-sm'})
        self.fields["block"].widget.attrs.update({'class':'form-control-sm'})
        self.fields["coverage"].widget.attrs.update({'class':'form-control-sm'})
        self.fields["log2r"].widget.attrs.update({'class':'form-control-sm'})
        self.fields["ref_read"].widget.attrs.update({'class':'form-control-sm'})
        self.fields["alt_read"].widget.attrs.update({'class':'form-control-sm'})
