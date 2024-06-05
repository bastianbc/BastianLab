from django import forms
from .models import NucAcids, AREA_NA_LINK
from barcodeset.models import Barcode
from areas.models import Areas
from core.forms import BaseForm


class NucAcidForm(BaseForm, forms.ModelForm):
    area = forms.ModelMultipleChoiceField(queryset=Areas.objects.all(),
                                          label="Area"
                                          )
    amount = forms.FloatField()

    class Meta:
        model = NucAcids
        fields = ("name", "date", "method", "na_type", "conc", "vol_init", "vol_remain", "notes", "area", )

    def __init__(self, *args, **kwargs):
        super(NucAcidForm, self).__init__(*args, **kwargs)
        self.fields["name"].required = False
        self.fields['area'].required = False

        if self.instance.pk:
            self.fields['area'].initial = self.instance.area_na_links.values_list('area', flat=True)

    def save(self, commit=True):
        instance = super(NucAcidForm, self).save(commit=False)
        if commit:
            instance.save()
        AREA_NA_LINK.objects.filter(nucacid=instance).delete()
        for area in self.cleaned_data['area']:
            AREA_NA_LINK.objects.create(
                nucacid=instance,
                area=area,
                input_vol=0,
                input_amount=0
            )
        return instance


class SampleLibCreationOptionsForm(forms.Form):
    barcode_start_with = forms.ModelChoiceField(queryset = Barcode.objects.filter(barcode_set__active=True))
    target_amount = forms.FloatField()
    shear_volume = forms.FloatField()
    prefix = forms.CharField()

class FilterForm(forms.Form):
    date_range = forms.DateField()
    na_type = forms.ChoiceField(choices=[('','---------' )] + NucAcids.NA_TYPES[:-1], label="NA Type", required=False)

    def __init__(self, *args, **kwargs):
        super(FilterForm, self).__init__(*args, **kwargs)
        self.fields["date_range"].widget.attrs.update({'class':'form-control-sm'})
        self.fields["na_type"].widget.attrs.update({'class':'form-control-sm'})
