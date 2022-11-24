from rest_framework import serializers
from .models import *
from lab.models import Patients

class AreasSerializer(serializers.ModelSerializer):
    num_nucacids = serializers.IntegerField()
    DT_RowId = serializers.SerializerMethodField()
    block = serializers.SerializerMethodField()
    project = serializers.SerializerMethodField()
    area_type = serializers.SerializerMethodField()
    investigator = serializers.SerializerMethodField()

    class Meta:
        model = Areas
        fields = ("ar_id", "name", "block", "project", "collection", "area_type", "completion_date", "investigator","num_nucacids", "DT_RowId",)

    def get_DT_RowId(self, obj):
        return getattr(obj, 'ar_id')

    def get_area_type(self,obj):
        return obj.get_area_type_display()

    def get_investigator(self, obj):
        return obj.block.project.pi if obj.block.project else None

    def get_block(self,obj):
        return obj.block.name if obj.block else None

    def get_project(self,obj):
        return obj.block.project.name if obj.block.project else None
