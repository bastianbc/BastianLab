from django import forms
from .models import *
from datetime import date, datetime
from core.forms import BaseForm

class AnalysisRunForm(BaseForm):
    sheet_content = forms.CharField(widget=forms.HiddenInput())

    class Meta:
        model = AnalysisRun
        fields = ("user", "pipeline", "genome")
        widgets = {
            "user": forms.HiddenInput(),
        }
