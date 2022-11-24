from rest_framework import serializers
from .models import *

class SampleLibSerializer(serializers.ModelSerializer):
    DT_RowId = serializers.SerializerMethodField()
    method = serializers.StringRelatedField()
    input_amount = serializers.SerializerMethodField()
    num_nucacids = serializers.IntegerField()

    class Meta:
        model = SampleLib
        fields = ("id", "name", "barcode", "date", "method", "conc", "input_amount", "vol_init", "vol_remain", "num_nucacids", "DT_RowId",)

    def get_DT_RowId(self, obj):
       return getattr(obj, 'id')

    def get_input_amount(self,obj):
        return round(obj.input_amount,2)

class UsedNuacidsSerializer(serializers.ModelSerializer):
    sample_lib = serializers.StringRelatedField()
    nucacid = serializers.StringRelatedField()

    class Meta:
        model = NA_SL_LINK
        fields = ("sample_lib", "nucacid", "input_vol", "input_amount", )
