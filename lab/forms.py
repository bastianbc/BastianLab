from django import forms
from .models import Patients
from blocks.models import Blocks

class PatientForm(forms.ModelForm):
    blocks = forms.ModelMultipleChoiceField(queryset=Blocks.objects.all(), label="Blocks", required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance', None)
        if instance:
            self.fields['blocks'].queryset = Blocks.objects.filter(patient=instance)
            self.fields['blocks'].initial = instance.patient_blocks.all()
        else:
            self.fields['blocks'].queryset = Blocks.objects.all()

    class Meta:
        model = Patients
        fields = ('pat_id', 'dob', 'sex', 'race', 'source', 'blocks', 'notes', 'consent')
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
            'dob': forms.DateInput(attrs={'type': 'date'}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        for block in self.cleaned_data.get('blocks', []):
            block.patient = instance
            block.save()
        return instance
    
class FilterForm(forms.Form):
    race = forms.ChoiceField(
        choices=[(0, '---------')] + list(Patients.RACE_TYPES),
        label="Race",
        required=False
    )
    sex = forms.ChoiceField(
        choices=[('', '---------')] + list(Patients.SEX_TYPES),
        label="Sex",
        required=False
    )
    dob = forms.IntegerField(label="Date of Birth", required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Stil sınıflarını ve Select2 entegrasyonunu ekle
        self.fields["race"].widget.attrs.update({'class': 'form-control-sm'})
        self.fields["sex"].widget.attrs.update({'class': 'form-control-sm'})
        self.fields["dob"].widget.attrs.update({'class': 'form-control-sm', 'placeholder': 'Year'})
        # Eğer bir seçim widget'ı için ekstra kontrol gerekiyorsa ekleyebilirsiniz
        self.fields["race"].widget.attrs["data-control"] = "select2"
        self.fields["sex"].widget.attrs["data-control"] = "select2"