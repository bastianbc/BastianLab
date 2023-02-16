from rest_framework import serializers
from .models import *

class NucacidsSerializer(serializers.ModelSerializer):
    # block = serializers.IntegerField()
    DT_RowId = serializers.SerializerMethodField()
    area = serializers.StringRelatedField()
    method_label = serializers.SerializerMethodField()
    na_type_label = serializers.SerializerMethodField()
    vol_remain = serializers.SerializerMethodField()
    amount = serializers.SerializerMethodField()

    class Meta:
        model = NucAcids
        fields = ("nu_id", "name", "area", "na_type", "na_type_label", "date", "method", "method_label", "conc", "vol_init", "vol_remain", "amount", "DT_RowId",)

    def get_DT_RowId(self, obj):
       return getattr(obj, 'nu_id')

    def get_method_label(self, obj):
        return obj.method.name if obj.method else None

    def get_na_type_label(self,obj):
        return obj.get_na_type_display()

    def get_area(self, obj):
        return obj.name

    def get_vol_remain(self, obj):
        return round(obj.vol_remain,2)

    def get_amount(self, obj):
        return round(obj.amount,2)
