from rest_framework import serializers
from .models import *

class NucacidsSerializer(serializers.ModelSerializer):
    # block = serializers.IntegerField()
    DT_RowId = serializers.SerializerMethodField()

    class Meta:
        model = NucAcids
        fields = ("nu_id", "area", "na_type", "date_extr", "method", "qubit", "volume", "amount", "re_ext", "total_ext", "na_sheared", "shearing_vol", "te_vol", "DT_RowId",)

    def get_DT_RowId(self, obj):
       return getattr(obj, 'nu_id')
