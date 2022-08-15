from django import forms
from django.forms import BaseModelFormSet, Textarea, ModelForm
from django.forms.models import BaseInlineFormSet, inlineformset_factory
from django.utils.translation import ugettext_lazy as _
from .models import Areas, NucAcids
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Row, Column
from django.forms import TextInput

# class NucAcidsForm(ModelForm):
#     class Meta:
#         fields = ('nu_id', 'na_type', 'date_extr', 'method', 'qubit', 'volume', 'amount',
#                     're_ext', 'total_ext', 'na_sheared', 'shearing_vol', 'te_vol', 'area'),
#         labels = {'nu_id': _('NA-ID'),
#                 'na_type': _('Type of NucAcid'),
#                 'date_extr': _('Extraction Date'),
#                 'method': _('Extraction Method'),
#                 'qubit': _('Qubit'),
#                 'volume': _('Volume'),
#                 'amount': _('Total Amount [ng]'),
#                 're_ext': _('Re-Extraction [ng]'),
#                 'total_ext': _('Total Extracted [ng]'),
#                 'na_sheared': _('NA Sheared [ng]'),
#                 'shearing_vol': _('Shearing Vol [µl]'),
#                 'te_vol': _('TE Vol [µl]')
#                 }
#         widgets = {'area': TextInput(attrs={'readonly': 'readonly'})
# }

class BaseNucAcids(BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        # print('Args: ', args, 'Kwargs', kwargs)
        super().__init__(*args, **kwargs)
        self.queryset = NucAcids.objects.order_by('-nu_id')[:4]

class NucAcidsFormSetHelper(FormHelper):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.form_method = 'post'
           
            self.layout = Layout(
            Row(
                Column('nu_id', css_class='form-group col-md-1 mb-0'),
                Column('na_type', css_class='form-group col-md-1 mb-0'),
                Column('date_extr', css_class='form-group col-md-1 mb-0'),
                Column('method', css_class='form-group col-md-1 mb-0'),
                css_class='form-row'
            ))
            
            # self.layout = Layout(Fieldset(
            #     'nu_id', 'na_type', 'date_extr', 'method', 'qubit', 'volume', 'amount',
            #         're_ext', 'total_ext', 'na_sheared', 'shearing_vol', 'te_vol',)
            # )
            self.form_show_labels = False
            self.error_text_inline = True
            # self.form_class = 'form-inline'
            # self.field_template = 'bootstrap4/layout/inline_field.html'
            # self.fields['date_extr'].label = False
            # self.render_required_fields = True
            self.add_input(Submit("submit", "Save"))