from rest_framework import serializers
from .models import *

class PatientsSerializer(serializers.ModelSerializer):
    num_blocks = serializers.IntegerField()
    DT_RowId = serializers.SerializerMethodField()
    sex = serializers.SerializerMethodField()
    race = serializers.SerializerMethodField()

    class Meta:
        model = Patients
        fields = ("pat_id","source","sex","race","date_added","num_blocks","DT_RowId",)

    def get_DT_RowId(self, obj):
        return getattr(obj, 'pa_id')

    def get_sex(self,obj):
        return obj.get_sex_display()

    def get_race(self,obj):
        return obj.get_race_display()
