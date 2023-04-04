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
    ))
    file = forms.FileField()

class SequencedFilesForm(forms.Form):
    checksum_file = forms.FileField()
    tree2_file = forms.FileField()
