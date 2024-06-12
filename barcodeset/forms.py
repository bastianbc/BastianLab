from django import forms
from .models import *

class NewBarcodesetForm(forms.ModelForm):
    file = forms.FileField(help_text='A CSV file that has columns of Name, I5 and I7')
    class Meta:
        model = Barcodeset
        fields = ("name",)

class EditBarcodesetForm(forms.ModelForm):
    class Meta:
        model = Barcodeset
        fields = ("name","active")
