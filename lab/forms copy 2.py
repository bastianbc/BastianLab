from django import forms
from django.forms import ModelForm
from crispy_forms.helper import FormHelper
from django.forms.models import BaseInlineFormSet, inlineformset_factory
from django.utils.translation import ugettext_lazy as _
from django.forms import Textarea
from .models import Patients, Blocks, Areas

def is_empty_form(form):
    # A form is considered empty if it passes its validation,
    # but doesn't have any data.
    # This is primarily used in formsets, when you want to
    # validate if an individual form is empty (extra_form).
    if form.is_valid() and not form.cleaned_data:
        return True
    else:
        # Either the form has errors (isn't valid) or
        # it doesn't have errors and contains data.
        return False


def is_form_persisted(form):
    # Does the form have a model instance attached and it's not being added?
    # e.g. The form is about an existing block whose data is being edited.
    if form.instance and not form.instance._state.adding:
        return True
    else:
        # Either the form has no instance attached or
        # it has an instance that is being added.
        return False


class PatientForm(ModelForm):
    #required_css_class = 'required'
    source = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Contributing Institution'}))
    class Meta:
        model = Patients
        fields = [
            'pat_id', 'dob', 'race', 'source', 'notes', 'project'
        ]
    
        labels = {
            'pat_id': _('Patient ID'),
        }
        help_texts = {
            'pat_id': _('Requires a unique identifier for each patient.'),
        }
        error_messages = {
            'pat_id': {
                'max_length': _("This patient's ID is too long."),
                'unique': _("This patient ID is already registered")
            },
        }

    
# class NameForm(forms.Form):
#     your_name = forms.CharField(label='Your name', max_length=100)

# class TpatsForm(ModelForm):
#     #required_css_class = 'required'
#     class Meta:
#         model = Tpats
#         fields = [
#             'name', 'age', 'source', 'notes'
#         ]




# The formset for editing the Areas that belong to a Block.
AreaFormset = inlineformset_factory(
                            Blocks,
                            Areas,
                            fields=('ar_id','collection', 'area_type', 'notes'),
                            
                            extra=1)
                            

class BaseBlocksWithAreasFormset(BaseInlineFormSet):
    # The base formset for editing blocks belonging to a Patient, and the
    # Areas belonging to those Blocks.
    # def __init__(self, *args, **kwargs):
    #     super(BaseBlocksWithAreasFormset, self).__init__(*args, **kwargs)
    #     self.blocksform.fields['old_block_id'].label = "New Email Label"

    def add_fields(self, form, index):
        super().add_fields(form, index)

        # Save the formset for a Block's Areas in the nested property.
        form.nested = AreaFormset(
                                instance=form.instance,
                                data=form.data if form.is_bound else None,
                                files=form.files if form.is_bound else None,
                                prefix='area-%s-%s' % (
                                    form.prefix,
                                    AreaFormset.get_default_prefix()),
                                )
        print(form.nested)

    def is_valid(self):
        # Also validate the nested formsets.
        result = super().is_valid()

        if self.is_bound:
            for form in self.forms:
                if hasattr(form, 'nested'):
                    result = result and form.nested.is_valid()

        return result

    def clean(self):
        # If a parent form has no data, but its nested forms do, we should
        # return an error, because we can't save the parent.
        # For example, if the Book form is empty, but there are Images.
        super().clean()

        for form in self.forms:
            if not hasattr(form, 'nested') or self._should_delete_form(form):
                continue

            if self._is_adding_nested_inlines_to_empty_form(form):
                form.add_error(
                    field=None,
                    error=_('You are trying to add area(s) to a block which '
                            'does not yet exist. Please add information '
                            'about the block and choose the area(s) again.'))

    def save(self, commit=True):
        # Also save the nested formsets.
        result = super().save(commit=commit)

        for form in self.forms:
            if hasattr(form, 'nested'):
                if not self._should_delete_form(form):
                    form.nested.save(commit=commit)

        return result

    def _is_adding_nested_inlines_to_empty_form(self, form):
        # Are we trying to add data in nested inlines to a form that has no data?
        # e.g. Adding Areas to a new Block whose data we haven't entered?
        if not hasattr(form, 'nested'):
            # A basic form; it has no nested forms to check.
            return False

        if is_form_persisted(form):
            # We're editing (not adding) an existing model.
            return False

        if not is_empty_form(form):
            # The form has errors, or it contains valid data.
            return False

        # All the inline forms that aren't being deleted:
        non_deleted_forms = set(form.nested.forms).difference(
            set(form.nested.deleted_forms)
        )

        # At this point we know that the "form" is empty.
        # In all the inline forms that aren't being deleted, are there any that
        # contain data? Return True if so.
        return any(not is_empty_form(nested_form) for nested_form in non_deleted_forms)

# This is the formset for the Blocks belonging to a Patient and the
# Areas belonging to those Blocks.
#
# You'd use this by passing in a Patient:
# PatientsBlocksWithImagesFormset(**form_kwargs, instance=self.object)
PatientsBlocksWithAreasFormset = inlineformset_factory(
                                Patients,
                                Blocks,
                                formset=BaseBlocksWithAreasFormset,
                                # We need to specify at least one Block field:
                                # exclude=('age', 'slides','slides_left', 'fixation', 'ulceration', 'area' 'pat_id'),
                                fields=('old_block_id','project'),
                                extra=1,
                                # If you don't want to be able to delete Patients:
                                #can_delete=False
                            )

