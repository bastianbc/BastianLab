from rest_framework import serializers
from .models import *

class NucacidsSerializer(serializers.ModelSerializer):
    # block = serializers.IntegerField()
    DT_RowId = serializers.SerializerMethodField()
    area_id = serializers.SerializerMethodField()
    area_name = serializers.SerializerMethodField()
    method_label = serializers.SerializerMethodField()
    na_type_label = serializers.SerializerMethodField()
    vol_remain = serializers.SerializerMethodField()
    amount = serializers.SerializerMethodField()
    num_samplelibs = serializers.IntegerField()

    class Meta:
        model = NucAcids
        fields = ("nu_id", "name", "area_id", "area_name", "na_type", "na_type_label", "date", "method", "method_label", "conc", "vol_init", "vol_remain", "amount", "num_samplelibs", "DT_RowId",)

    def get_DT_RowId(self, obj):
       return getattr(obj, 'nu_id')

    def get_method_label(self, obj):
        return obj.method.name if obj.method else None

    def get_na_type_label(self,obj):
        return obj.get_na_type_display()

    def get_area_name(self, obj):
        return obj.area.name if obj.area else None

    def get_area_id(self, obj):
        return obj.area.ar_id if obj.area else None

    def get_vol_remain(self, obj):
        return round(obj.vol_remain,2)

    def get_amount(self, obj):
        return round(obj.amount,2)
