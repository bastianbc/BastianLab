from rest_framework import serializers
from .models import *

class PatientsSerializer(serializers.ModelSerializer):
    num_blocks = serializers.IntegerField()
    DT_RowId = serializers.SerializerMethodField()

    class Meta:
        model = Patients
        fields = ("pat_id","source","sex","race","project","date_added","num_blocks","DT_RowId",)

    def get_DT_RowId(self, obj):
        return getattr(obj, 'pa_id')
