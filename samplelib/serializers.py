from rest_framework import serializers
from .models import *

class SampleLibSerializer(serializers.ModelSerializer):
    DT_RowId = serializers.SerializerMethodField()
    method = serializers.StringRelatedField()
    amount_in = serializers.SerializerMethodField()
    num_nucacids = serializers.IntegerField()
    barcode = serializers.StringRelatedField()

    class Meta:
        model = SampleLib
        fields = ("id", "name", "barcode", "date", "method", "amount_final", "qpcr_conc", "amount_in", "vol_init", "vol_remain", "pcr_cycles", "qubit", "num_nucacids", "DT_RowId",)

    def get_DT_RowId(self, obj):
       return getattr(obj, 'id')

    def get_amount_in(self,obj):
        return round(obj.amount_in,2)

class UsedNuacidsSerializer(serializers.ModelSerializer):
    sample_lib = serializers.StringRelatedField()
    nucacid = serializers.StringRelatedField()

    class Meta:
        model = NA_SL_LINK
        fields = ("sample_lib", "nucacid", "input_vol", "input_amount", )

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
