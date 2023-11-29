from django import forms
from .models import SequencingFile, SequencingFileSet


class SequencingFileForm(forms.ModelForm):
    class Meta:
        model = SequencingFile
        fields = "__all__"


class SequencingFileSetForm(forms.ModelForm):
    class Meta:
        model = SequencingFileSet
        fields = "__all__"
