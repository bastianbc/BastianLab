from rest_framework import serializers
from .models import *
from libprep.serializers import AreaLinksSerializer, NucacidsSerializer
from libprep.models import NucAcids

class NaSlLinkSerializer(serializers.ModelSerializer):
    area_na_link = serializers.SerializerMethodField()
    class Meta:
        model = NA_SL_LINK
        fields = ('nucacid','area_na_link',)

    def get_area_na_link(self, obj):
        return (obj.nucacid.area_na_links.all()) if obj.nucacid else None

    def get_area_na_link(self, obj):
        # Assuming obj.nucacid.area_na_links.all() returns a QuerySet of AREA_NA_LINK instances
        area_na_links = obj.nucacid.area_na_links.all() if obj.nucacid else None
        if area_na_links is not None:
            # Use the serializer to serialize the QuerySet
            serializer = AreaLinksSerializer(area_na_links, many=True)
            return serializer.data
        return None

class SampleLibSerializer(serializers.ModelSerializer):
    na_sl_links = NaSlLinkSerializer(read_only=True, many=True)
    DT_RowId = serializers.SerializerMethodField()
    method_label = serializers.SerializerMethodField()
    amount_in = serializers.SerializerMethodField()
    amount_final = serializers.SerializerMethodField()
    num_nucacids = serializers.IntegerField()
    barcode = serializers.StringRelatedField()
    area_id = serializers.SerializerMethodField()
    area_num = serializers.IntegerField()
    num_blocks = serializers.IntegerField()
    num_capturedlibs = serializers.IntegerField()

    class Meta:
        model = SampleLib
        fields = ("id", "name", "barcode", "area_id",
                  "area_num","date", "method", "method_label",
                  "amount_final", "qpcr_conc", "amount_in", "vol_init",
                  "vol_remain", "pcr_cycles", "qubit", "num_blocks",
                  "num_nucacids", "num_capturedlibs", "DT_RowId", "na_sl_links",)

    def get_DT_RowId(self, obj):
       return getattr(obj, 'id')

    def get_amount_in(self,obj):
        return round(obj.amount_in,2)

    def get_amount_final(self,obj):
        return round(obj.amount_final,2)

    def get_area_name(self, obj):
        return obj.area.name if obj.area else None

    def get_area_id(self, obj):
        # Nuclecic Acids have to be from the SAME Area (never many areas) to be combined into one SL.
        # return obj.na_sl_links.first().nucacid.name if obj.na_sl_links.count() > 0 else None
        # return obj.na_sl_links.all().nucacid.area.ar_id if obj.na_sl_links.count() > 0 and obj.na_sl_links.first().nucacid.area else None
        return None

    def get_area_name(self,obj):
        # Nuclecic Acids have to be from the SAME Area (never many areas) to be combined into one SL.
        # return obj.na_sl_links.first().nucacid.area.name if obj.na_sl_links.count() > 0 and obj.na_sl_links.first().nucacid.area else None
        return None

    def get_method_label(self,obj):
        return obj.method.name if obj.method else None

class UsedNuacidsSerializer(serializers.ModelSerializer):
    sample_lib_id = serializers.SerializerMethodField()
    sample_lib_name = serializers.SerializerMethodField()
    nucacid_id = serializers.SerializerMethodField()
    nucacid_name = serializers.SerializerMethodField()
    input_amount = serializers.SerializerMethodField()
    input_vol = serializers.SerializerMethodField()

    class Meta:
        model = NA_SL_LINK
        fields = ("sample_lib_id", "sample_lib_name", "nucacid_id", "nucacid_name", "input_vol", "input_amount", )

    def get_input_amount(self,obj):
        return round(obj.input_amount,2)

    def get_input_vol(self,obj):
        return round(obj.input_vol,2)

    def get_sample_lib_id(self,obj):
        return obj.sample_lib.id

    def get_sample_lib_name(self,obj):
        return obj.sample_lib.name

    def get_nucacid_id(self,obj):
        return obj.nucacid.nu_id

    def get_nucacid_name(self,obj):
        return obj.nucacid.name

class SavedNuacidsSerializer(serializers.ModelSerializer):
    sample_lib = serializers.StringRelatedField()
    nucacid = serializers.StringRelatedField()
    area = serializers.SerializerMethodField()
    conc = serializers.SerializerMethodField()
    input_vol = serializers.SerializerMethodField()
    input_amount = serializers.SerializerMethodField()

    class Meta:
        model = NA_SL_LINK
        fields = ("id", "sample_lib", "nucacid", "area", "conc", "input_vol", "input_amount", )

    def get_area(self,obj):
        return obj.nucacid.area.name

    def get_conc(self,obj):
        return obj.nucacid.conc

    def get_input_vol(self,obj):
        return round(obj.input_vol,2)

    def get_input_amount(self,obj):
        return round(obj.input_amount,2)
