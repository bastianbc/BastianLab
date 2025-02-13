from django import forms
from .models import Patient
from blocks.models import Block

class PatientForm(forms.ModelForm):
    block = forms.ModelMultipleChoiceField(queryset=Block.objects.all(), label="Blocks", required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance', None)
        self.fields["block"].widget.attrs.update({'class': 'form-control-sm'})
        self.fields["block"].widget.attrs["data-control"] = "select2"
        if instance:
            self.fields['block'].queryset = Block.objects.filter(patient=instance)
            self.fields['block'].initial = instance.patient_blocks.all()
        else:
            self.fields['block'].queryset = Block.objects.all()

    class Meta:
        model = Patient
        fields = ('pat_id', 'dob', 'sex', 'race', 'source', 'block', 'notes', 'consent')
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
            'dob': forms.NumberInput(attrs={'min': 1900, 'placeholder': 'Year'}),
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
        choices=[(0, '---------')] + list(Patient.RACE_TYPES),
        label="Race",
        required=False
    )
    sex = forms.ChoiceField(
        choices=[('', '---------')] + list(Patient.SEX_TYPES),
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
