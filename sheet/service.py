from samplelib.models import SampleLib
from samplelib.serializers import SampleLibSerializer
from rest_framework import serializers
from areas.models import Areas
import csv
from django.http import HttpResponse


class SampleLibSerializerManual(serializers.ModelSerializer):
    class Meta:
        model = SampleLib
        fields = "__all__"


class CustomSampleLibSerializer(serializers.ModelSerializer):
    method_label = serializers.SerializerMethodField()
    barcode = serializers.StringRelatedField()
    na_type = serializers.SerializerMethodField()
    area_type = serializers.SerializerMethodField()
    patient = serializers.SerializerMethodField()
    matching_normal_sl = serializers.SerializerMethodField()

    class Meta:
        model = SampleLib
        fields = ("id", "name",  "shear_volume",  "qpcr_conc", "barcode", "na_type", "area_type", "method", "method_label", "patient", "matching_normal_sl")

    def get_method_label(self,obj):
        return obj.method.name if obj.method else None

    def get_na_type(self, obj):
        return obj.na_sl_links.first().nucacid.na_type if len(obj.na_sl_links.all())>0 else None

    def get_area_type(self, obj):
        area_type=[]
        if obj.na_sl_links.all():
            for na_sl_link in obj.na_sl_links.all():
                if na_sl_link.nucacid.area_na_links.all():
                    for area_na_link in na_sl_link.nucacid.area_na_links.all():
                        area = area_na_link.area
                        if area.name == "UndefinedArea":
                            continue
                        if area.area_type:
                            at = "Normal" if area.area_type.lower() == "normal" else "Tumor"
                            if at not in area_type:
                                area_type.append(at)
        return area_type

    def get_patient(self, obj):
        if obj.na_sl_links.first():
            nuc_acid = obj.na_sl_links.first().nucacid
            if nuc_acid.area_na_links.first():
                area = nuc_acid.area_na_links.first().area
                if area:
                    patient = area.block.patient.pat_id
                    return patient
        return None

    def get_matching_normal_sl(self, obj):
        matching_normal_sl=[]
        if obj.na_sl_links.all():
            for na_sl_link in obj.na_sl_links.all():
                if na_sl_link.nucacid.area_na_links.all():
                    for area_na_link in na_sl_link.nucacid.area_na_links.all():
                        area = area_na_link.area
                        if area.name == "UndefinedArea":
                            continue
                        if area.area_type:
                            at = "Normal" if area.area_type.lower() == "normal" else "Tumor"
                            if at == "Tumor":
                                patient = area.block.patient
                                matching_normal = Areas.objects.filter(block__patient=patient, area_type="normal")
                                matching_normal_sl = SampleLib.objects.filter(na_sl_links__nucacid__area_na_links__area__in=matching_normal).values("name").distinct()
                                matching_normal_sl = SampleLibSerializerManual(matching_normal_sl, many=True).data
            # print(matching_normal_sl)
            return matching_normal_sl
        return None

def get_sample_lib_list(request):
    samplelibs = SampleLib.query_by_args(
        **request.GET,
        user=request.user,
        sequencing_run=[False],
        barcode=[False],
        i5=[False],
        i7=[False],
        area_type=[False],
        bait=[False])
    serializer = CustomSampleLibSerializer(samplelibs['items'], many=True)
    result = dict()
    result['data'] = serializer.data
    return result

