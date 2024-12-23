from django import forms
from bait.models import Bait
from barcodeset.models import Barcode
from sequencingrun.models import SequencingRun
from lab.models import Patient

class FilterForm(forms.Form):
    sequencing_run = forms.ModelMultipleChoiceField(
        queryset=SequencingRun.objects.filter(sequencing_libs__cl_seql_links__captured_lib__sl_cl_links__sample_lib__isnull=False).distinct().order_by("name"),
        label="Sequencing Run"
    )
    patient = forms.ModelChoiceField(
        queryset=Patient.objects.filter(
            patient_blocks__block_areas__area_na_links__nucacid__na_sl_links__sample_lib__isnull=False
        ).distinct().order_by("pat_id"))
    barcode = forms.ModelChoiceField(queryset=Barcode.objects.filter())
    bait = forms.ModelChoiceField(queryset=Bait.objects.filter())
    area_type = forms.ChoiceField(choices=[('','---------' ),("normal","Normal"),("tumor","Tumor")], label="Area Type", required=False)
    na_type = forms.ChoiceField(choices=[('','---------' ),("dna","DNA"),("rna","RNA")], label="NA Type", required=False)

    def __init__(self, *args, **kwargs):
        super(FilterForm, self).__init__(*args, **kwargs)
        self.fields["sequencing_run"].widget.attrs.update({'class':'form-control-sm'})
        self.fields["sequencing_run"].widget.attrs["data-control"] = "select2"
        self.fields["patient"].widget.attrs.update({'class':'form-control-sm'})
        self.fields["patient"].widget.attrs["data-control"] = "select2"
        self.fields["barcode"].widget.attrs.update({'class':'form-control-sm'})
        self.fields["bait"].widget.attrs.update({'class':'form-control-sm'})
        self.fields["area_type"].widget.attrs.update({'class':'form-control-sm'})
        self.fields["na_type"].widget.attrs.update({'class':'form-control-sm'})


class ReportForm(forms.Form):
    sequencing_run_report = forms.ModelChoiceField(
        queryset=SequencingRun.objects.filter(sequencing_libs__cl_seql_links__captured_lib__sl_cl_links__sample_lib__isnull=False).distinct().order_by("name"),
        label="Sequencing Run"
    )
    sequencing_run_report_multiple = forms.ModelMultipleChoiceField(
        queryset=SequencingRun.objects.filter(sequencing_libs__cl_seql_links__captured_lib__sl_cl_links__sample_lib__isnull=False).distinct().order_by("name"),
        label="Sequencing Run Multiple Selection"
    )

    def __init__(self, *args, **kwargs):
        super(ReportForm, self).__init__(*args, **kwargs)
        self.fields["sequencing_run_report"].widget.attrs.update({'class':'form-control-sm'})
        self.fields["sequencing_run_report"].widget.attrs["data-control"] = "select2"
        self.fields["sequencing_run_report_multiple"].widget.attrs.update({'class':'form-control-sm'})
        self.fields["sequencing_run_report_multiple"].widget.attrs["data-control"] = "select2"
