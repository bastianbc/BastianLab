from django import forms
from .models import Patients

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patients
        fields = ('pat_id', 'dob', 'sex', 'race', 'source', 'notes',)
