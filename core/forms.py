from django import forms

class BaseForm(forms.ModelForm):
    """
    Makes forms compatible with bootstrap. All forms are derived from this base form.
    """
    def __init__(self, *args, **kwargs):
        super(BaseForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["autocomplete"] = "off"
            if type(visible.field.widget) not in [forms.widgets.CheckboxInput,forms.widgets.SelectMultiple]:
                visible.field.widget.attrs['class'] = "form-control form-control-solid"
            if type(visible.field.widget) == forms.widgets.SelectMultiple:
                visible.field.widget.attrs['class'] = "form-select form-select-solid"
                visible.field.widget.attrs['data-control'] = "select2"
                visible.field.widget.attrs['data-close-on-select'] = "false"
                visible.field.widget.attrs['data-placeholder'] = "Select an option"
                visible.field.widget.attrs['data-allow-clear'] = "true"
            # if type(visible.field) == forms.fields.TypedChoiceField or type(visible.field) == forms.models.ModelChoiceField or type(visible.field) == forms.ChoiceField:
            #     visible.field.widget.attrs["data-control"] = "select2"
            # if type(visible.field)==forms.fields.DateTimeField:
            #     visible.field.widget.attrs['class'] += ' sat-datetime'
            # if type(visible.field)==forms.fields.DateField:
            #     visible.field.widget.attrs['class'] += ' sat-date'
