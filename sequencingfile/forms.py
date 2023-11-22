from django import forms
from .models import SequencingFile

class SequencingFileForm(forms.ModelForm):
    class Meta:
        model = SequencingFile
        fields = "__all__"
