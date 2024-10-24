from rest_framework import serializers
from .models import *
from lab.models import Patients

class AreasSerializer(serializers.ModelSerializer):
    num_nucacids = serializers.IntegerField()
    DT_RowId = serializers.SerializerMethodField()
    num_blocks = serializers.IntegerField()
    num_projects = serializers.IntegerField()
    area_type_label = serializers.SerializerMethodField()
    # collection_label = serializers.SerializerMethodField()
    investigator = serializers.SerializerMethodField()
    num_samplelibs = serializers.IntegerField()

    class Meta:
        model = Areas
        fields = ("ar_id", "name", "num_blocks", "num_projects", "area_type", "area_type_label", "completion_date", "investigator","num_nucacids", "num_samplelibs", "DT_RowId",)
        # "collection","collection_label",
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
        return obj.block.project.name if obj.block.project else None
