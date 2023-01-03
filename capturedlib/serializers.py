from rest_framework import serializers
from .models import *

class CapturedLibSerializer(serializers.ModelSerializer):
    DT_RowId = serializers.SerializerMethodField()
    bait_label = serializers.SerializerMethodField()
    buffer_label = serializers.SerializerMethodField()

    class Meta:
        model = CapturedLib
        fields = ("id", "name", "date", "bait", "bait_label", "buffer", "buffer_label", "frag_size", "conc", "amp_cycle", "nm", "vol_init", "vol_remain", "amount", "pdf", "DT_RowId",)

    def get_DT_RowId(self, obj):
       return getattr(obj, 'id')

    def get_bait_label(self,obj):
        return obj.bait.name if obj.bait else None

    def get_buffer_label(self,obj):
        return obj.buffer.name if obj.buffer else None

class UsedSampleLibSerializer(serializers.ModelSerializer):
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
        return obj.sample_lib.qpcr_conc

    def get_vol_remain(self, obj):
        return obj.sample_lib.vol_remain

    def get_barcode(self, obj):
        return obj.sample_lib.barcode.name
