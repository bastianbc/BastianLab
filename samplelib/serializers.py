from rest_framework import serializers
from .models import *

class SampleLibSerializer(serializers.ModelSerializer):
    # block = serializers.IntegerField()
    DT_RowId = serializers.SerializerMethodField()
    method = serializers.StringRelatedField()

    class Meta:
        model = SampleLib
        fields = ("id", "name", "barcode", "date", "method", "te_vol", "input_amount", "vol_init", "vol_remain", "DT_RowId",)

    def get_DT_RowId(self, obj):
       return getattr(obj, 'id')

class UsedNuacidsSerializer(serializers.ModelSerializer):
    sample_lib = serializers.StringRelatedField()
    nucacid = serializers.StringRelatedField()

    class Meta:
        model = NA_SL_LINK
        fields = ("sample_lib", "nucacid", "input_vol", "input_amount", )
