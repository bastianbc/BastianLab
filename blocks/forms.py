from django import forms
from .models import *
from body.models import Body
from django.core.exceptions import ValidationError
from core.forms import BaseForm

class BlockForm(BaseForm, forms.ModelForm):
    # mock_body_site = forms.ModelChoiceField(queryset = Body.objects.filter(parent=None), label="Body Site", required=False)

    class Meta:
        model = Blocks
        fields = "__all__"
        widgets = {"body_site": forms.HiddenInput()}

    def __init__(self, *args, **kwargs):
        super(BlockForm, self).__init__(*args, **kwargs)
        # self.fields["patient"].required = True

    def clean(self):
        """
        The algorithm created for the body site throws a weird exception. This error is caught and removed.
        """
        if "body_site" in dict(self.errors.items()).keys():
            del self.errors["body_site"]
        return self.cleaned_data

class AreaCreationForm(forms.Form):
    # area_type = forms.ChoiceField(choices=Areas.AREA_TYPE_TYPES)
    number = forms.IntegerField(initial=1, label="How many areas for block do you want to create?")


class BlockUrlForm(forms.ModelForm):
    class Meta:
        model = BlockUrl
        fields = "__all__"

    def clean_url(self):
        data = self.cleaned_data["url"]
        if not data.endswith("/"):
            raise ValidationError("URL needs to be ended with /")
        return data