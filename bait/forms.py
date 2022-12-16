from django import forms
from .models import *

class BaitForm(forms.ModelForm):
    class Meta:
        model = Bait
        fields = ("name",)
