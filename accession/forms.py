from django import forms
from django.forms import ModelForm, Textarea, ClearableFileInput, ModelChoiceField, TextInput
from django.utils.translation import ugettext_lazy as _
from lab.models import Blocks, Areas
from django.contrib.auth.models import User
from projects.models import Projects
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Div, HTML, Fieldset, MultiField, Field, Button
from crispy_forms.bootstrap import InlineField, FormActions


class BlockForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
    required_css_class = 'required'
    class Meta:
        model = Blocks
        fields = [
            'old_block_id', 'clinical', 'icd9','gross','micro','notes','body_site', 'age', 'diagnosis', 'mitoses', 'p_stage', 'prim', 'subtype',
            'thickness'
        ]
        widgets = {'notes': Textarea(attrs={'rows': 3, 'cols': 40}),
                    'micro': Textarea(attrs={'rows': 3, 'cols': 40}),
                    'gross': Textarea(attrs={'rows': 3, 'cols': 40}),
                    'body_site': Textarea(attrs={'rows': 1, 'cols': 20}),
                    'icd9': Textarea(attrs={'rows': 1, 'cols': 20}),
                    'diagnosis': Textarea(attrs={'rows': 1, 'cols': 20}),
                    'prim': Textarea(attrs={'rows': 1, 'cols': 20}),
                    'p_stage': Textarea(attrs={'rows': 1, 'cols': 20}),
                    'subtype': Textarea(attrs={'rows': 1, 'cols': 20})
                 }
        
        labels = {
            'old_block_id': _('Path Nr.'),
            'body_site': _('Body Site'),
            'icd9': _('ICD-9'),
            'age': _('Age [years]'),
            'prim': _('Primary [yes/no]'),
            'p_stage': _('pT Stage'),
            'mitoses': _('Mitoses/mm2'),
            'thickness': _('Thickness [mm]'),
            'diagnosis': _('Diagnosis'),
            # 'project_id': _('Project')
        }
        help_texts = {
            'old_block_id': _('Requires a unique identifier for each Block.'),
        }
        error_messages = {
            'old_block_id': {
                'max_length': _("This block ID is too long."),
                'unique': _("This block is already registered")
            },
        }

class AreaForm(ModelForm):
    investigator = ModelChoiceField(queryset=User.objects.all(),label='Microdissected by', required=False)
    old_area_id = forms.CharField(required=True, label='Area ID', help_text='Must be unique', widget=forms.TextInput(attrs={'size':'40', 'autocomplete':'off'}))
    def __init__(self, *args, **kwargs):
        # projectid = kwargs.pop('projectid')
        initial_old_area_id = kwargs.pop('next_old_area_id')
        super().__init__(*args, **kwargs)
        self.fields['old_area_id'].initial = initial_old_area_id

        self.helper = FormHelper()
        # self.helper.form_class = 'form-inline'
        # self.helper.field_template = 'bootstrap4/layout/inline_field.html'
        # self.helper.label_class = 'col-lg-4'
        # self.helper.field_class = 'col-lg-4'
        self.helper.layout = Layout(
            # MultiField(
            #     'Add areas to Block {{blockid}} with Diagnosis: {{dx}}',
            #     Div(
            #     'old_area_id',
            #     'area_type',
            #     'collection',
            #     'investigator',
            #     css_id = 'special-fields'
            #     ),
            #     'image',
            #     'notes' 
            # # ),
            # # InlineField('old_area_id'
            #     # 'Add areas to Block {{blockid}} with Diagnosis: {{dx}}',
            #     'old_area_id',
            #     'area_type',
            #     Field('collection', css_class="custom-select"),
            #     Field('investigator', css_class="col-md-2"),
            #     # 'investigator',
            #     # 'image',
            #     # 'notes' 
            # # ),
            Div(HTML("<h3>Add new Area of Block {{blockid}} to Project {{projectabb}}</h3>"),),
            Div(HTML("<p>Diagnosis for this Block: {{dx}}</p>"),),
            'old_area_id',
            'area_type',
            'collection',
            'investigator',
            'image',
            HTML("""{% if form.instance.image.value %}<img class="img-responsive" src="form.instance.image.value }}">{% endif %}""", ),
            # HTML('<img src="{{ areas.image.url }}">'),

            'notes',

            # Row(
            #     Column('old_area_id', css_class='form-group col-md-3 mb-0'),
            #     Column('area_type', css_class='form-group col-md-3 mb-0'),
            #     Column('collection', css_class='form-group col-md-3 mb-0'),
            #     Column('investigator', css_class='form-group col-md-3 mb-0'),
            #     css_class='form-row'
            # ),
            # Row(
            #     Column('image', css_class='form-group col-md-6 mb-0'),
            #     # HTML("""{% if form.image.value %}<img class="img-responsive" src="{{ MEDIA_URL }}{{ form.image.value }}">{% endif %}""", ),
            #     HTML('<img src="{{ areas.image.url }}">'),
            #     Column('notes', css_class='form-group col-md-6 mb-0'),
            #     css_class='form-row'
            # ),
            Submit('submit', 'Add Area'),
            HTML("""<button class="btn btn-link" onclick="javascript:history.back();">Cancel</button>""")
            # HTML("""<input type="submit" onclick="window.l ocation='{% url 'form:main' %}' ; return false;" value="Cancel>""")
            # Button('cancel', 'Cancel', css_class = 'btn btn-default')
        )
    required_css_class = 'required'
    class Meta:
        model = Areas
        fields = [
            'old_area_id', 'collection', 'area_type', 'image', 'investigator', 'notes', 'block'
        ]        
        labels = {
            'old_area_id': _('Area ID'),
            'collection': _('Collection method'),
            'area_type': _('Type of area'),
            'image': _('Image'),
            'investigator': _('Dissector')
            # 'project_id': _('Project')
        }
        help_texts = {
            'old_area_id': _('Requires a unique identifier for each Area.'),
        }
        error_messages = {
            'old_area_id': {
                'max_length': _("This area ID is too long."),
                'unique': _("This area is already registered")
            },
        }

    # self.helper.add_input(Button('cancel', 'Cancel', css_class='btn-primary',
    #                             onclick="window.location.href = '{}';".format(reverse('your-cancel-url-name'))))

class AreaUpdateForm(ModelForm):
    investigator = ModelChoiceField(queryset=User.objects.all(), label='Microdissected by', required=False)
    # old_area_id = forms.CharField(required=True, label='Area ID', help_text='Must be unique', widget=forms.TextInput(attrs={'size':'40', 'autocomplete':'off'}))
    def __init__(self, *args, **kwargs):
        investigator_default = kwargs.pop('investigator_default')
        super().__init__(*args, **kwargs)
        if investigator_default:
            investigator_object=User.objects.get(username=investigator_default)
            self.initial['investigator'] = investigator_object
            # need to pass User object into the form's initial. Passing it into the field's initial like below
            # does NOT work:
            # self.fields['investigator'].initial = investigator_object
        self.helper = FormHelper()
        # self.helper.form_class = 'form-inline'
        # self.helper.field_template = 'bootstrap4/layout/inline_field.html'
        # self.helper.label_class = 'col-lg-4'
        # self.helper.field_class = 'col-lg-4'
        self.helper.layout = Layout(
            Div(HTML("<h3>Modify Area of Block {{areas.block.old_block_id}} in Project {{areas.block.project.abbreviation}}</h3>"),),
            Div(HTML("<p>Diagnosis for this Block: {{areas.block.diagnosis}}</p>"),),
            Row(
                Column('old_area_id', css_class='form-group col-md-3 mb-0'),
                Column('area_type', css_class='form-group col-md-3 mb-0'),
                Column('collection', css_class='form-group col-md-3 mb-0'),
                Column('investigator', css_class='form-group col-md-3 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('image', css_class='form-row'),
            ),
            Row(Column('notes', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Update Area'),
            HTML("""<a href="{% url 'area-delete' areas.ar_id %}?projectid={{areas.block.project.pr_id}}" class="btn btn-danger" role="button"> Delete Area</a>"""),

        )
    # required_css_class = 'required'
    class Meta:
        model = Areas
        fields = [
            'old_area_id', 'block', 'collection', 'area_type', 'image', 'investigator', 'notes', 'block'
        ]        
        labels = {
            'old_area_id': _('Area ID'),
            'collection': _('Collection method'),
            'area_type': _('Type of area'),
            'image': _('Image'),
            'investigator': _('Dissector')
            # 'project_id': _('Project')
        }
        help_texts = {
            'old_area_id': _('Requires a unique identifier for each Area.'),
        }
        error_messages = {
            'old_area_id': {
                'max_length': _("This area ID is too long."),
                'unique': _("This area is already registered")
            },
        }

    # self.helper.add_input(Button('cancel', 'Cancel', css_class='btn-primary',
    #                             onclick="window.location.href = '{}';".format(reverse('your-cancel-url-name'))))