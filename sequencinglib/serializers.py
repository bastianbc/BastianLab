from rest_framework import serializers
from .models import *

class SequencingLibSerializer(serializers.ModelSerializer):
    # block = serializers.IntegerField()
    DT_RowId = serializers.SerializerMethodField()
    buffer = serializers.SerializerMethodField()
    nmol = serializers.SerializerMethodField()

    class Meta:
        model = SequencingLib
        fields = ("id", "name", "date", "nmol", "buffer", "pdf", "DT_RowId",)

    def get_DT_RowId(self, obj):
       return getattr(obj, 'id')

    def get_nmol(self,obj):
        return round(obj.nmol,2)

    def get_buffer(self,obj):
        return obj.get_buffer_display()

class UsedCapturedLibSerializer(serializers.ModelSerializer):
    # captured_lib = serializers.StringRelatedField()
    name = serializers.SerializerMethodField()
    conc = serializers.SerializerMethodField()
    vol_remain = serializers.SerializerMethodField()
    frag_size = serializers.SerializerMethodField()
    nm = serializers.SerializerMethodField()
    nmol = serializers.SerializerMethodField()
    target_vol = serializers.SerializerMethodField()

    class Meta:
        model = CL_SEQL_LINK
        fields = ("id", "captured_lib", "name", "conc", "frag_size", "vol_remain", "nm", "nmol", "target_vol", "volume",)

    def get_name(self, obj):
        return obj.captured_lib.name

    def get_conc(self, obj):
        return obj.captured_lib.conc

    def get_vol_remain(self, obj):
        return obj.captured_lib.vol_remain

    def get_frag_size(self, obj):
        return obj.captured_lib.frag_size

    def get_nm(self, obj):
        return round(obj.captured_lib.nm,2)

    def get_nmol(self,obj):
        return obj.sequencing_lib.nmol

    def get_target_vol(self,obj):
        return obj.sequencing_lib.target_vol
