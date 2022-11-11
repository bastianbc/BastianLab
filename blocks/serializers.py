from rest_framework import serializers
from .models import *
from lab.models import Patients

class BlocksSerializer(serializers.ModelSerializer):
    num_areas = serializers.IntegerField()
    patient = serializers.StringRelatedField()
    DT_RowId = serializers.SerializerMethodField()
    project = serializers.StringRelatedField()

    class Meta:
        model = Blocks
        fields = ("bl_id","name","project","patient","diagnosis","body_site","thickness","num_areas","DT_RowId",)

    def get_value(self,obj):
        return obj.patient.pat_id

    def get_DT_RowId(self, obj):
           return getattr(obj, 'bl_id')

    def get_project(self, obj):
        return obj.project.name
