from django import forms
from .models import Projects
from core.forms import BaseForm
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import CharField, Value
from django.db.models.functions import Concat
from blocks.models import Blocks
User = get_user_model()

class ProjectForm(BaseForm):
    blocks = forms.ModelMultipleChoiceField(queryset=Blocks.objects.all(),
                                          label="Blocks"
                                          )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["technician"].queryset = User.objects.filter(groups__name=settings.TECHNICIAN_GROUP_NAME)
        self.fields['technician'].label_from_instance = lambda obj: "%s" % obj.get_full_name()
        self.fields["researcher"].queryset = User.objects.filter(groups__name=settings.RESEARCHER_GROUP_NAME)
        self.fields['researcher'].label_from_instance = lambda obj: "%s" % obj.get_full_name()

    class Meta:
        model = Projects
        fields = [
            'pr_id', 'name', 'abbreviation', 'blocks', 'description', 'speedtype', 'pi', 'date_start', 'technician', 'researcher',
        ]
        widgets = {'description': forms.Textarea(attrs={'rows': 4, 'cols': 40})}

    def save(self, commit=True):
        instance = super(ProjectForm, self).save(commit=False)
        if commit:
            instance.save()
        Blocks.objects.filter(project=instance)
        for block in self.cleaned_data['blocks']:
            block.project = instance
            block.save()
        return instance

class FilterForm(forms.Form):
    date_range = forms.DateField(label="Start Date")
    pi = forms.ChoiceField(choices=[('','---------' )] + Projects.PI_CHOICES, label="Private Investigator", required=False)
    technician = forms.ModelChoiceField(queryset=User.objects.filter(
            groups__name='Technicians',
            technician_projects__isnull=False
            ).distinct()
        )
    researcher = forms.ModelChoiceField(queryset=User.objects.filter(
            groups__name='Researchers',
            researcher_projects__isnull=False
            ).distinct()
        )


    def __init__(self, *args, **kwargs):
        super(FilterForm, self).__init__(*args, **kwargs)
        self.fields["date_range"].widget.attrs.update({'class':'form-control-sm'})
        self.fields["pi"].widget.attrs.update({'class':'form-control-sm'})
        self.fields["technician"].widget.attrs.update({'class':'form-control-sm'})
        self.fields["technician"].widget.attrs["data-control"] = "select2"
        self.fields['technician'].label_from_instance = lambda obj: f"{obj.first_name} {obj.last_name}"
        self.fields["researcher"].widget.attrs.update({'class':'form-control-sm'})
        self.fields["researcher"].widget.attrs["data-control"] = "select2"
        self.fields['researcher'].label_from_instance = lambda obj: f"{obj.first_name} {obj.last_name}"

