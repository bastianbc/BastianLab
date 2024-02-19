from django import forms
from .models import *
from core.forms import BaseForm

class BodyForm(BaseForm, forms.ModelForm):
    class Meta:
        model = Body
        fields = ("name","parent")
