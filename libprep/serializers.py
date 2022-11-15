from rest_framework import serializers
from .models import *

class NucacidsSerializer(serializers.ModelSerializer):
    # block = serializers.IntegerField()
    DT_RowId = serializers.SerializerMethodField()
    area = serializers.StringRelatedField()
    method = serializers.StringRelatedField()
    na_type = serializers.SerializerMethodField()
    vol_remain = serializers.SerializerMethodField()

    class Meta:
        model = NucAcids
        fields = ("nu_id", "name", "area", "na_type", "date", "method", "conc", "vol_init", "vol_remain", "amount", "DT_RowId",)

    def get_DT_RowId(self, obj):
       return getattr(obj, 'nu_id')

    def get_method(self, obj):
        return obj.name

    def get_na_type(self,obj):
        return obj.get_na_type_display()

    def get_area(self, obj):
        return obj.name

    def get_vol_remain(self, obj):
        return round(obj.vol_remain,2)
