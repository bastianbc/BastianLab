from rest_framework import serializers
from .models import *

class CapturedLibSerializer(serializers.ModelSerializer):
    # block = serializers.IntegerField()
    DT_RowId = serializers.SerializerMethodField()
    barcode = serializers.StringRelatedField()
    nm = serializers.SerializerMethodField()
    bait = serializers.SerializerMethodField()

    class Meta:
        model = CapturedLib
        fields = ("id", "name", "barcode", "date", "bait", "frag_size", "conc", "amp_cycle", "buffer", "nm", "vol_init", "vol_remain", "amount", "DT_RowId",)

    def get_DT_RowId(self, obj):
       return getattr(obj, 'id')

    def get_nm(self,obj):
        return round(obj.nm,2)

    def get_bait(self,obj):
        return obj.get_bait_display()

class UsedSampleLibSerializer(serializers.ModelSerializer):
    # captured_lib = serializers.StringRelatedField()
    id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    conc = serializers.SerializerMethodField()
    vol_remain = serializers.SerializerMethodField()
    barcode = serializers.SerializerMethodField()
    volume = serializers.FloatField()

    class Meta:
        model = SL_CL_LINK
        fields = ("captured_lib", "id","name", "conc", "vol_remain", "barcode", "volume", "amount", )

    def get_id(self, obj):
        return obj.sample_lib.id

    def get_name(self, obj):
        return obj.sample_lib.name

    def get_conc(self, obj):
        return obj.sample_lib.conc

    def get_vol_remain(self, obj):
        return obj.sample_lib.vol_remain

    def get_barcode(self, obj):
        return obj.sample_lib.barcode.name
