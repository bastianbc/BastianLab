from django import forms
from .models import SampleQC
from samplelib.models import SampleLib
from sequencingrun.models import SequencingRun
from variant.models import VariantFile

class SampleQCForm(forms.ModelForm):
    sample_lib = forms.ModelChoiceField(
        queryset=SampleLib.objects.filter(qc_metrics__isnull=False).distinct().order_by("name"),
        label="Sample Library", required=False
    )
    sequencing_run = forms.ModelChoiceField(
        queryset=SequencingRun.objects.filter(qc_metrics__isnull=False).distinct().order_by("name"),
        label="Sequencing Run", required=False
    )

    variant_file = forms.ModelChoiceField(
        queryset=VariantFile.objects.filter(qc_metrics__isnull=False).distinct().order_by("name"),
        label="Variant file", required=False
    )

    class Meta:
        model = SampleQC
        fields = '__all__'
