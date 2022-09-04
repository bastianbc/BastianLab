from django import forms
from .models import *

class BlockForm(forms.ModelForm):
    class Meta:
        model = Blocks
        fields = "__all__"
