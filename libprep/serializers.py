from rest_framework import serializers
from .models import *

class NucacidsSerializer(serializers.ModelSerializer):
    # block = serializers.IntegerField()
    DT_RowId = serializers.SerializerMethodField()

    class Meta:
        model = NucAcids
        fields = ("nu_id", "name", "area", "na_type", "date", "method", "qubit", "vol_init", "vol_remain", "DT_RowId",)

    def get_DT_RowId(self, obj):
       return getattr(obj, 'nu_id')
