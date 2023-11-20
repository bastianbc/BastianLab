from django import forms
from .models import *
from body.models import Body

class BlockForm(forms.ModelForm):
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
