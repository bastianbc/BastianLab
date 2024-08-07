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
        widgets = {
            "body_site": forms.HiddenInput(),
            "diagnosis": forms.Textarea(attrs={'rows':2, 'style':'resize:none;'}),
            "clinical": forms.Textarea(attrs={'rows':2, 'style':'resize:none;'}),
            "gross": forms.Textarea(attrs={'rows':2,'style':'resize:none;'}),
            "path_note": forms.Textarea(attrs={'rows':4,'style':'resize:none;'}),
            "micro": forms.Textarea(attrs={'rows':4,'style':'resize:none;'}),
            "notes": forms.Textarea(attrs={'rows':4,'style':'resize:none;'}),
        }

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


class FilterForm(forms.Form):
    p_stage = forms.ChoiceField(choices=[('','---------' )] + list(Blocks.P_STAGE_TYPES), label="P_STAGE", required=False)
    prim = forms.ChoiceField(choices=[('','---------' )] + list(Blocks.PRIM_TYPES), label="PRIM", required=False)
    # collection = forms.ChoiceField(choices=[('','---------' )] + list(Blocks.COLLECTION_CHOICES), label="COLLECTION", required=False)
    body_site = forms.ModelChoiceField(queryset=Body.objects.all())


    def __init__(self, *args, **kwargs):
        super(FilterForm, self).__init__(*args, **kwargs)
        self.fields["p_stage"].widget.attrs.update({'class':'form-control-sm'})
        self.fields["prim"].widget.attrs.update({'class':'form-control-sm'})
        # self.fields["collection"].widget.attrs.update({'class':'form-control-sm'})
        self.fields["body_site"].widget.attrs.update({'class':'form-control-sm'})
        self.fields["body_site"].widget.attrs["data-control"] = "select2"
