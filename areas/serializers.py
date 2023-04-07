from rest_framework import serializers
from .models import *
from lab.models import Patients

class AreasSerializer(serializers.ModelSerializer):
    num_nucacids = serializers.IntegerField()
    DT_RowId = serializers.SerializerMethodField()
    block_id = serializers.SerializerMethodField()
    block_name = serializers.SerializerMethodField()
    project_id = serializers.SerializerMethodField()
    project_name = serializers.SerializerMethodField()
    area_type_label = serializers.SerializerMethodField()
    # collection_label = serializers.SerializerMethodField()
    investigator = serializers.SerializerMethodField()

    class Meta:
        model = Areas
        fields = ("ar_id", "name", "block_id", "block_name", "project_id", "project_name", "area_type", "area_type_label", "completion_date", "investigator","num_nucacids", "DT_RowId",)

    def get_DT_RowId(self, obj):
        return getattr(obj, 'ar_id')

    def get_area_type_label(self,obj):
        return obj.get_area_type_display()

    def get_investigator(self, obj):
        return obj.block.project.pi if obj.block.project else None

    def get_block_name(self,obj):
        return obj.block.name if obj.block else None

    def get_block_id(self,obj):
        return obj.block.bl_id if obj.block else None

    def get_project_id(self,obj):
        return obj.block.project.pr_id if obj.block.project else None

    def get_project_name(self,obj):
        return obj.block.project.pat_id if obj.block.project else None
