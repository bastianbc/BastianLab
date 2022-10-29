from rest_framework import serializers
from .models import *

class SequencingLibSerializer(serializers.ModelSerializer):
    # block = serializers.IntegerField()
    DT_RowId = serializers.SerializerMethodField()
    buffer = serializers.StringRelatedField()
    nmol = serializers.SerializerMethodField()

    class Meta:
        model = SequencingLib
        fields = ("id", "name", "date", "nmol", "buffer", "DT_RowId",)

    def get_DT_RowId(self, obj):
       return getattr(obj, 'id')

    def get_nmol(self,obj):
        return round(obj.nmol,2)

class UsedCapturedLibSerializer(serializers.ModelSerializer):
    # captured_lib = serializers.StringRelatedField()
    id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    conc = serializers.SerializerMethodField()
    vol_remain = serializers.SerializerMethodField()
    barcode = serializers.SerializerMethodField()
    volume = serializers.FloatField()

    class Meta:
        model = CL_SEQL_LINK
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
