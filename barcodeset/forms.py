from django import forms
from .models import *

class NewBarcodesetForm(forms.ModelForm):
    file = forms.FileField()
    class Meta:
        model = Barcodeset
        fields = ("name",)

class EditBarcodesetForm(forms.ModelForm):
    class Meta:
        model = Barcodeset
        fields = ("name","active")
