from django import forms
from .models import Patients

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patients
        fields = ('pat_id', 'dob', 'sex', 'race', 'source', 'notes', 'consent')


class FilterForm(forms.Form):
    race = forms.ChoiceField(choices=[(0,'---------' )] + list(Patients.RACE_TYPES), label="Race", required=False)
    sex = forms.ChoiceField(choices=[('','---------' )] + list(Patients.SEX_TYPES), label="Sex", required=False)
    dob = forms.IntegerField(label="Date of Birth", required=False)



    def __init__(self, *args, **kwargs):
        super(FilterForm, self).__init__(*args, **kwargs)
        self.fields["race"].widget.attrs.update({'class':'form-control-sm'})
        self.fields["sex"].widget.attrs.update({'class':'form-control-sm'})
        self.fields["dob"].widget.attrs.update({'class':'form-control-sm'})
