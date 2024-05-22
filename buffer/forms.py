from django import forms
from .models import *

class BufferForm(forms.ModelForm):
    class Meta:
        model = Buffer
        fields = ("name",)
