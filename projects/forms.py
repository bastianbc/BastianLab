from django import forms
from .models import Projects
from core.forms import BaseForm
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import CharField, Value
from django.db.models.functions import Concat

User = get_user_model()

class ProjectForm(BaseForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # self.fields["pi"].widget.attrs['class'] = 'form-control'

        self.fields["technician"].queryset = User.objects.filter(groups__name=settings.TECHNICIAN_GROUP_NAME)
        self.fields['technician'].label_from_instance = lambda obj: "%s" % obj.get_full_name()

        self.fields["researcher"].queryset = User.objects.filter(groups__name=settings.RESEARCHER_GROUP_NAME)
        self.fields['researcher'].label_from_instance = lambda obj: "%s" % obj.get_full_name()

    class Meta:
        model = Projects
        fields = [
            'pr_id', 'name', 'abbreviation', 'description', 'speedtype', 'pi', 'date_start', 'technician', 'researcher',
        ]
        widgets = {'description': forms.Textarea(attrs={'rows': 4, 'cols': 40})}
