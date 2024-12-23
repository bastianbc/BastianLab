from rest_framework import serializers
from .models import *

class PatientsSerializer(serializers.ModelSerializer):
    num_blocks = serializers.IntegerField()
    DT_RowId = serializers.SerializerMethodField()
    sex_label = serializers.SerializerMethodField()
    race_label = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = ("id","pat_id","source","sex","race","sex_label","race_label","date_added","num_blocks","DT_RowId",)

    def get_DT_RowId(self, obj):
        return getattr(obj, 'id')

    def get_sex_label(self,obj):
        return obj.get_sex_display()

    def get_race_label(self,obj):
        return obj.get_race_display()
