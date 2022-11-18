from django import forms
from .models import *
from areas.models import Areas

class BlockForm(forms.ModelForm):
    class Meta:
        model = Blocks
        fields = "__all__"

class AreaCreationForm(forms.Form):
    # area_type = forms.ChoiceField(choices=Areas.AREA_TYPE_TYPES)
    number = forms.IntegerField(initial=1, label="How many areas for block do you want to create?")
