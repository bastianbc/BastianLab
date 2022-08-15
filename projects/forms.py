from django import forms
from django.forms import ModelForm, Textarea
from django.utils.translation import ugettext_lazy as _
from .models import Projects
from crispy_forms.helper import FormHelper


class ProjectForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
    required_css_class = 'required'
    # source = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Contributing Institution'}))
    class Meta:
        model = Projects
        fields = [
            'pr_id', 'name', 'abbreviation', 'description', 'speedtype', 'pi', 'date_start'
        ]
        widgets = {'description': Textarea(attrs={'rows': 5,
                                  'cols': 40})}
        
        labels = {
            'pr_id': _('Project ID'),
            'pi': _('Principal Investigator'),
            'date_start': _('Project Start Date')
        }
        help_texts = {
            'abbreviation': _('Requires a unique identifier for each Project.'),
        }
        error_messages = {
            'abbreviation': {
                'max_length': _("This abbreviation is too long."),
                'unique': _("This abbreviation is already registered")
            },
        }