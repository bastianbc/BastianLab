from django import forms
from .models import *

class MigrationForm(forms.Form):
    app = forms.ChoiceField(choices = (
        ("project", "Project"),
        ("patient", "Patient"),
        ("block", "Block"),
        ("area", "Area"),
        ("na", "NA"),
        ("sl", "SL"),
        ("cl", "CL"),
        ("seql", "SeqL"),
        ("seqr", "SeqR"),
        ("barcode", "Barcode"),
        ("sf", "SequencingFile"),
        ("variant", "Variant"),
        ("md5", "MD5 Summary"),
    ))
    file = forms.FileField()

class SequencedFilesForm(forms.Form):
    checksum_file = forms.FileField()
    tree2_file = forms.FileField()

class VariantForm(forms.Form):
    file = forms.FileField()

class GeneForm(forms.Form):
    file = forms.FileField()

class LookupAllDataForm(forms.Form):
    consolidated_data_file = forms.FileField()
    md5_summary_file = forms.FileField()
    tree2_file = forms.FileField()
    checksum_dataset = forms.FileField()

class ConsolidatedDataForm(forms.Form):
    consolidated_data_file = forms.FileField()
    md5_summary_file = forms.FileField()
    # tree2_file = forms.FileField()
    # checksum_dataset = forms.FileField()
    # old_pat_id_file = forms.FileField()

class BodySitesForm(forms.Form):
    file = forms.FileField()

class AirtableConsolidatedDataForm(forms.Form):
    file = forms.FileField()
