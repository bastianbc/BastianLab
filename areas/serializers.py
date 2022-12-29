from rest_framework import serializers
from .models import *
from lab.models import Patients

class AreasSerializer(serializers.ModelSerializer):
    num_nucacids = serializers.IntegerField()
    DT_RowId = serializers.SerializerMethodField()
    block = serializers.SerializerMethodField()
    project = serializers.SerializerMethodField()
    area_type_label = serializers.SerializerMethodField()
    collection_label = serializers.SerializerMethodField()
    investigator = serializers.SerializerMethodField()

    class Meta:
        model = Areas
        fields = ("ar_id", "name", "block", "project", "collection", "collection_label", "area_type", "area_type_label", "completion_date", "investigator","num_nucacids", "DT_RowId",)

    def get_DT_RowId(self, obj):
        return getattr(obj, 'ar_id')

    def get_area_type_label(self,obj):
        return obj.get_area_type_display()

    def get_collection_label(self,obj):
        return obj.get_collection_display()

    def get_investigator(self, obj):
        return obj.block.project.pi if obj.block.project else None

    def get_block(self,obj):
        return obj.block.name if obj.block else None

    def get_project(self,obj):
        return obj.block.project.name if obj.block.project else None
