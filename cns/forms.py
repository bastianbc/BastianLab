from django import forms
from samplelib.models import SampleLib
from areas.models import Area
from blocks.models import Block
from sequencingrun.models import SequencingRun
from lab.models import Patient
from cns.models import Cns
from gene.models import Gene

class FilterForm(forms.Form):
    chromosome = forms.ChoiceField(label="Chromosome", required=False)
    log2 = forms.IntegerField(label="log2", required=False)
    chr_start = forms.IntegerField(label="chr_start", required=False)
    chr_end = forms.IntegerField(label="chr_end", required=False)
    sample_library = forms.ModelChoiceField(
        queryset=SampleLib.objects.filter(samplelib_cns__isnull=False).distinct().order_by("name"),
        label="Sample Library", required=False
    )
    sequencing_run = forms.ModelChoiceField(
        queryset=SequencingRun.objects.filter(sequencingrun_cns__isnull=False).distinct().order_by("name"),
        label="Sequencing Run", required=False
    )
    gene = forms.CharField(label="Gene", required=False)


    def __init__(self, *args, **kwargs):
        super(FilterForm, self).__init__(*args, **kwargs)
        self.fields["sequencing_run"].widget.attrs.update({'class': 'form-control-sm'})
        self.fields["sequencing_run"].widget.attrs["data-control"] = "select2"
        self.fields["sample_library"].widget.attrs.update({'class': 'form-control-sm'})
        self.fields["sample_library"].widget.attrs["data-control"] = "select2"
        self.fields["chromosome"].widget.attrs.update({'class': 'form-control-sm'})
        self.fields["chromosome"].widget.attrs["data-control"] = "select2"
        chromosome_choices = [('', '-------')] + [
            (f"chr{i}", f"chr{i}") for i in range(1, 24)
        ] + [
                                 ("chrX", "chrX"),
                                 ("chrY", "chrY"),
                             ]

        self.fields['chromosome'].choices = chromosome_choices
