from django import forms
from django.forms import BaseModelFormSet, Textarea, ModelForm
from django.forms.models import BaseInlineFormSet, inlineformset_factory
from django.forms.widgets import DateInput, TextInput
from django.utils.translation import ugettext_lazy as _
from .models import NucAcids
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, HTML, Div
# from django.forms import TextInput

class NucAcidsForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Update Nucleic Acid'))
        # self.helper.form_class = 'form-inline'
        self.helper.field_template = 'bootstrap4/layout/multifield.html'
        # self.helper.form_class = 'form-horizontal'
        # self.helper.label_class = 'col-lg-2'
        # self.helper.field_class = 'col-lg-8'
        self.helper.layout = Layout(
            Fieldset(
                'You are editing Nucleic Acid {{ nucacids.nu_id }}',
                    Div('na_type', 'date_extr','method',
                        css_id = 'special-fields'),
                    Div('qubit','volume','amount'),
                    Div('re_ext','total_ext','na_sheared'),
                    Div('shearing_vol','te_vol', 'area')
                )
            )
        # self.helper.layout = Layout(
        #     'na_type',
        #     'date_extr',
        #     'method',
        #     )
    required_css_class = 'required'
    class Meta:
        model = NucAcids

        fields = ['nu_id', 'na_type', 'date_extr', 'method', 'qubit', 'volume', 'amount',
                    're_ext', 'total_ext', 'na_sheared', 'shearing_vol', 'te_vol', 'area']
        labels = {'nu_id': _('NA-ID'),
                'na_type': _('Type of NucAcid'),
                'date_extr': _('Extraction Date'),
                'method': _('Extraction Method'),
                'qubit': _('Qubit'),
                'volume': _('Volume'),
                'amount': _('Total Amount [ng]'),
                're_ext': _('Re-Extraction [ng]'),
                'total_ext': _('Total Extracted [ng]'),
                'na_sheared': _('NA Sheared [ng]'),
                'shearing_vol': _('Shearing Vol [µl]'),
                'te_vol': _('TE Vol [µl]')
                }
        widgets = {'area': TextInput(attrs={'readonly': 'readonly'}),
                }
        Submit('search', 'Update')

class BaseNucAcids(BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        # print('Args: ', args, 'Kwargs', kwargs)
        super().__init__(*args, **kwargs)
        self.queryset = NucAcids.objects.filter(na_type__isnull=True).order_by('-nu_id')
        #

class NucAcidsFormSetHelper(FormHelper):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.form_method = 'post'
            self.form_show_labels = True
            self.render_required_fields = True

class ExtractNucleicAcids(forms.Form):
    D='DNA'
    R='RNA'
    DR='DNA + RNA'
    NA_CHOICES= [(D, 'DNA'), (R, 'RNA'), (DR, 'DNA + RNA')]
    QAP='Qiagen AllPrep DNA/RNA Mini Kit'
    QFC='Qiagen FFPE DNA columns'
    PCI='PCI'
    METHOD_CHOICES = [(QAP, 'Qiagen AllPrep DNA/RNA Mini Kit'), (QFC,'Qiagen FFPE DNA columns'),
    (PCI,'PCI')]
    na_type = forms.ChoiceField(choices =NA_CHOICES, required=True, label='What type(s) of Nucleic Acid are you extracting?')
    prefix = forms.CharField(required=True, label='Choose a prefix for the unique ID of your Nucleic Acids', \
        help_text='e.g. AM will become AM-D-x for each new DNA, with x as an autoincrementing number', widget=forms.TextInput(attrs={'size':'40', 'autocomplete':'off'}))
    method = forms.ChoiceField(choices =METHOD_CHOICES, required=True, label='What method are you using?')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.field_class = 'col-lg-4'
        self.helper.layout = Layout(
            Div(HTML("<h3>You selected the following areas for nucleic acid extraction:</h3>\
            <ul>{% for area in area_list%} <li class='list-group-item'>{{area}}</lir> {% endfor %}</ul>"),),
            'na_type',
            'method',
            'prefix',
            Submit('submit', 'Create NucAcids')
        )
