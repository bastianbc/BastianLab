from django import forms
from .models import Projects
from core.forms import BaseForm

class ProjectForm(BaseForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["pi"].widget.attrs['class'] = 'form-control'

    class Meta:
        model = Projects
        fields = [
            'pr_id', 'name', 'abbreviation', 'description', 'speedtype', 'pi', 'date_start'
        ]
        widgets = {'description': forms.Textarea(attrs={'rows': 4, 'cols': 40})}
