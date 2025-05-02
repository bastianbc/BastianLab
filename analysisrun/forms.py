from django import forms
from .models import *
from datetime import date, datetime
from core.forms import BaseForm

class AnalysisRunForm(BaseForm):
    class Meta:
        model = AnalysisRun
        fields = ("pipeline", "genome")


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['pipeline'].required = True
        self.fields['genome'].required = True
