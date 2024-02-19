from django import forms
from .models import SequencingFile, SequencingFileSet
from core.forms import BaseForm

class SequencingFileForm(BaseForm, forms.ModelForm):
    class Meta:
        model = SequencingFile
        fields = "__all__"


class SequencingFileSetForm(BaseForm,forms.ModelForm):
    class Meta:
        model = SequencingFileSet
        fields = "__all__"

    # def __init__(self, *args, **kwargs):
    #     super(SequencingFileSetForm, self).__init__(*args, **kwargs)
    #     for visible in self.visible_fields():
    #         if type(visible.field) == forms.fields.TypedChoiceField or type(visible.field) == forms.models.ModelChoiceField or type(visible.field) == forms.ChoiceField:
    #             visible.field.widget.attrs["data-control"] = "select2"
