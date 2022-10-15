from rest_framework import serializers
from .models import *

class SampleLibSerializer(serializers.ModelSerializer):
    # block = serializers.IntegerField()
    DT_RowId = serializers.SerializerMethodField()

    class Meta:
        model = SampleLib
        fields = ("id", "name", "barcode", "date", "method", "te_vol", "input_amount", "vol_init", "vol_remain", "DT_RowId",)

    def get_DT_RowId(self, obj):
       return getattr(obj, 'id')
