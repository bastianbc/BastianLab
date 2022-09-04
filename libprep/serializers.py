from rest_framework import serializers
from .models import *

class NucacidsSerializer(serializers.ModelSerializer):
    class Meta:
        model = NucAcids
        fields = ("nu_id", "area", "block", "na_type", "date_extr", "method", "qubit", "volume", "amount", "re_ext", "total_ext", "na_sheared", "shearing_vol", "te_vol", )
